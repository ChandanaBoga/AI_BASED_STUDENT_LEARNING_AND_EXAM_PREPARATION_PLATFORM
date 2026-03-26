import json
import os
import asyncio
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import ollama
import uvicorn
import logging
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ai_service")

app = FastAPI()

# CORS: wildcard "*" and allow_credentials=True cannot be used together.
# Using explicit localhost origins for dev - extend this list for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allows file:// (null origin) pages to connect
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static File Serving ---
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "combined_app.html"))

@app.get("/combined_app.html")
async def read_combined_app():
    return FileResponse(os.path.join(FRONTEND_DIR, "combined_app.html"))

# Mount assets and other static files
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

# --- Proctor Proxy ---
PROCTOR_BASE_URL = "http://localhost:5050"

@app.post("/analyze")
async def proxy_analyze(request: Request):
    async with httpx.AsyncClient() as client:
        body = await request.json()
        try:
            resp = await client.post(f"{PROCTOR_BASE_URL}/analyze", json=body, timeout=60.0)
            return resp.json()
        except Exception as e:
            logger.error(f"Error proxying to proctor service: {e}")
            raise HTTPException(status_code=502, detail="Proctor service unreachable")

@app.get("/proctor/health")
async def proxy_health():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{PROCTOR_BASE_URL}/health", timeout=10.0)
            return resp.json()
        except Exception as e:
            logger.error(f"Error checking proctor health: {e}")
            raise HTTPException(status_code=502, detail="Proctor service unreachable")


class ChatRequest(BaseModel):
    message: str
    context: str = ""


class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "moderate"
    num_questions: int = 3


class UserProfile(BaseModel):
    fullname: str
    age: str
    dob: str
    year: str
    semester: str
    roll: str
    performance: Optional[Dict[str, Any]] = None


# Load knowledge base
KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.json")
knowledge_base_data = {}

def load_knowledge_base():
    global knowledge_base_data
    try:
        if os.path.exists(KNOWLEDGE_BASE_PATH):
            with open(KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as f:
                knowledge_base_data = json.load(f)
            print(f"Knowledge base loaded from {KNOWLEDGE_BASE_PATH}")
        else:
            print(f"Knowledge base not found at {KNOWLEDGE_BASE_PATH}")
    except Exception as e:
        print(f"  Error loading knowledge base: {e}")

load_knowledge_base()


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Prepare context from knowledge base
        logger.info(f"Received chat request: {request.message[:50]}...")
        kb_context = json.dumps(knowledge_base_data, indent=2)
        
        system_content = (
            "You are 'Btech Box AI', a professional academic assistant for TKR College of Engineering and Technology (TKRCET). "
            "You provide accurate, helpful, and concise information based on the provided knowledge base. "
            "For general academic topics (like DBMS, OS, etc.), you can use your general knowledge, but for college-specific facts (faculties, fees, timings), rely ONLY on the data below.\n\n"
            "### COLLEGE KNOWLEDGE BASE:\n"
            f"{kb_context}\n\n"
            "### RESPONSE GUIDELINES:\n"
            "1. **Accuracy**: Use the provided knowledge base for ALL college-specific facts. If unsure about a college detail, specify where to get info (e.g., 'Check the Admin Block').\n"
            "2. **Formatting**: Use **bold** for key terms and bullet points for lists of 2+ items.\n"
            "3. **Tone**: Professional, encouraging, and academic.\n"
            "4. **Links**: Include Markdown links [Title](URL) if present in the data.\n"
            "5. **Brevity**: 2-4 sentences max unless a detailed process or academic explanation (like generating questions) is requested.\n"
            "6. **Closing**: End with a unique encouraging remark and an emoji."
        )

        # ollama imported at module level
        logger.info("Calling Ollama...")
        response = await asyncio.wait_for(
            asyncio.to_thread(
                ollama.chat, 
                model='llama3.2:3b', 
                messages=[
                    {
                        'role': 'system',
                        'content': system_content
                    },
                    {
                        'role': 'user',
                        'content': request.message,
                    },
                ]
            ),
            timeout=300.0
        )
        logger.info("Ollama responded successfully.")
        return {"response": response.message.content}
    except asyncio.TimeoutError:
        logger.error("Ollama timeout after 300 seconds.")
        raise HTTPException(status_code=504, detail="AI service timed out.")
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _extract_json_from_llm_response(raw: str) -> str:
    """
    Robustly strips markdown code fences from LLM output.
    Handles: ```json\\n[...]```, ```\\n[...]```, or plain JSON.
    """
    raw = raw.strip()
    if raw.startswith("```"):
        # Remove the opening fence line (e.g., ```json or ```)
        first_newline = raw.find("\n")
        if first_newline != -1:
            raw = raw[first_newline + 1:]
        # Remove the closing fence
        if raw.endswith("```"):
            raw = raw[:-3]
    return raw.strip()


@app.post("/generate_quiz")
async def generate_quiz(request: QuizRequest):
    try:
        logger.info(f"Received quiz request for topic: {request.topic}")
        is_institutional = any(word in request.topic.lower() for word in ["tkr", "college", "admission", "fee", "hostel", "principal"])
        
        kb_part = f"KNOWLEDGE BASE:\n{kb_context}\n" if is_institutional else ""
        
        system_prompt = (
            "You are a quiz generation engine for TKRCET. "
            f"{kb_part}"
            "Output ONLY a valid JSON array of objects. No preamble, no markdown markers."
        )

        prompt = (
            f"Generate a {request.difficulty} difficulty quiz about '{request.topic}' with exactly {request.num_questions} questions. "
            "JSON structure: [{\"question\": \"...\", \"options\": [\"...\", \"...\", \"...\", \"...\"], \"correctAnswer\": 0-3}]. "
            "No extra text, just the array."
        )

        # ollama imported at module level
        logger.info("Calling Ollama for quiz generation...")
        response = await asyncio.wait_for(
            asyncio.to_thread(
                ollama.chat,
                model='llama3.2:3b',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt}
                ]
            ),
            timeout=300.0
        )
        logger.info("Ollama responded for quiz.")

        raw_content = response.message.content
        clean_content = _extract_json_from_llm_response(raw_content)

        try:
            quiz_json = json.loads(clean_content)
            return {"quiz": quiz_json}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from LLM: {clean_content}")
            return {"error": "Failed to parse quiz JSON", "raw": clean_content}

    except asyncio.TimeoutError:
        logger.error("Ollama quiz timeout after 300 seconds.")
        raise HTTPException(status_code=504, detail="Quiz generation timed out.")
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))


USERS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "users")

@app.post("/save_user")
async def save_user(profile: UserProfile):
    try:
        if not os.path.exists(USERS_DIR):
            os.makedirs(USERS_DIR)
        
        filename = f"{profile.fullname.replace(' ', '_').lower()}.json"
        path = os.path.join(USERS_DIR, filename)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(profile.model_dump(), f, indent=2)
        
        return {"status": "success", "message": f"User {profile.fullname} saved."}
    except Exception as e:
        print(f"Error saving user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/load_user/{fullname}")
async def load_user(fullname: str):
    try:
        filename = f"{fullname.replace(' ', '_').lower()}.json"
        path = os.path.join(USERS_DIR, filename)
        
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error loading user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "llama3.2:3b"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
