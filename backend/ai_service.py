import json
import os
import asyncio
from typing import Dict, Any, Optional, AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


# --- Models ---
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
    notes: Optional[List[Dict[str, Any]]] = None
    theme: Optional[str] = None


# --- Knowledge Base ---
KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.json")
knowledge_base_data = {}

def load_knowledge_base():
    global knowledge_base_data
    try:
        if os.path.exists(KNOWLEDGE_BASE_PATH):
            with open(KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as f:
                knowledge_base_data = json.load(f)
            logger.info(f"Knowledge base loaded from {KNOWLEDGE_BASE_PATH}")
        else:
            logger.warning(f"Knowledge base not found at {KNOWLEDGE_BASE_PATH}")
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")

load_knowledge_base()

# College-specific trigger keywords
COLLEGE_KEYWORDS = [
    "tkr", "tkrcet", "college", "admission", "fee", "hostel",
    "principal", "faculty", "department", "campus", "canteen",
    "library", "timing", "schedule", "contact", "address",
    "hod", "aiml", "csm", "cse", "ece", "eee", "it", "mech", "civil",
    "secretary", "chairman", "vice principal", "dean"
]

def build_chat_context(message: str) -> str:
    """
    Returns a compact KB snippet only when the user's message is college-specific.
    For general questions (DBMS, OS, algorithms…) we skip the KB entirely to keep
    the prompt short and get a much faster response.
    """
    msg_lower = message.lower()
    is_college_query = any(kw in msg_lower for kw in COLLEGE_KEYWORDS)

    if not is_college_query or not knowledge_base_data:
        return ""

    # Build a compact summary (max ~1500 chars) instead of dumping the whole file
    lines = []
    char_budget = 1500
    for key, value in knowledge_base_data.items():
        snippet = f"{key}: {json.dumps(value)}"
        if len(snippet) > 1200:
            snippet = snippet[:1200] + "…"
        lines.append(snippet)
        char_budget -= len(snippet)
        if char_budget <= 0:
            break

    return "\n".join(lines)


def build_system_prompt(kb_snippet: str) -> str:
    base = (
        "You are 'Btech Box AI', a professional academic assistant for TKR College of Engineering and Technology (TKRCET). "
        "You provide accurate, helpful, and concise information. "
        "For general academic topics (DBMS, OS, algorithms, programming…) use your general knowledge. "
        "For college-specific facts (faculty, fees, timings) rely ONLY on the data below if provided.\n"
    )
    if kb_snippet:
        base += f"\n### COLLEGE DATA (compact):\n{kb_snippet}\n"
    base += (
        "\n### GUIDELINES:\n"
        "1. Use **bold** for key terms and bullet points for lists.\n"
        "2. Keep responses to 2-4 sentences unless a detailed explanation is requested.\n"
        "3. End with a short encouraging remark and an emoji."
    )
    return base


# --- Chat (non-streaming, backward-compat) ---
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"[/chat] message: {request.message[:60]}")
        kb_snippet = build_chat_context(request.message)
        system_content = build_system_prompt(kb_snippet)

        response = await asyncio.wait_for(
            asyncio.to_thread(
                ollama.chat,
                model='llama3.2:3b',
                messages=[
                    {'role': 'system', 'content': system_content},
                    {'role': 'user',   'content': request.message},
                ]
            ),
            timeout=120.0   # reduced: if it hasn't finished in 2 min, something is wrong
        )
        logger.info("[/chat] Ollama responded.")
        return {"response": response.message.content}
    except asyncio.TimeoutError:
        logger.error("[/chat] Timeout after 120 s")
        raise HTTPException(status_code=504, detail="AI service timed out.")
    except Exception as e:
        logger.error(f"[/chat] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Chat (streaming SSE) ---
async def _stream_ollama(message: str) -> AsyncIterator[str]:
    """Yields SSE-formatted chunks from Ollama's streaming API."""
    kb_snippet = build_chat_context(message)
    system_content = build_system_prompt(kb_snippet)

    def _sync_stream():
        return ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': system_content},
                {'role': 'user',   'content': message},
            ],
            stream=True
        )

    try:
        stream = await asyncio.to_thread(_sync_stream)
        for chunk in stream:
            token = chunk.message.content or ""
            if token:
                # SSE format: data: <payload>\n\n
                payload = json.dumps({"token": token})
                yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"[/chat/stream] Error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    logger.info(f"[/chat/stream] message: {request.message[:60]}")
    return StreamingResponse(
        _stream_ollama(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering if behind a proxy
        }
    )


# --- Quiz Generation ---
def _extract_json_from_llm_response(raw: str) -> str:
    """Robustly extracts JSON array from LLM output using regex."""
    raw = raw.strip()
    # Try to find the first '[' and last ']' for an array
    import re
    match = re.search(r'(\[.*\])', raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback to the original cleaning logic if regex fails
    if raw.startswith("```"):
        first_newline = raw.find("\n")
        if first_newline != -1:
            raw = raw[first_newline + 1:]
        if raw.endswith("```"):
            raw = raw[:-3]
    return raw.strip()


@app.post("/generate_quiz")
async def generate_quiz(request: QuizRequest):
    try:
        logger.info(f"[/generate_quiz] topic={request.topic}, n={request.num_questions}")
        is_institutional = any(w in request.topic.lower() for w in COLLEGE_KEYWORDS)

        # Build a compact KB snippet only for institutional topics
        kb_part = ""
        if is_institutional and knowledge_base_data:
            lines = []
            budget = 600
            for k, v in knowledge_base_data.items():
                snippet = f"{k}: {json.dumps(v)}"[:250]
                lines.append(snippet)
                budget -= len(snippet)
                if budget <= 0:
                    break
            kb_part = "KNOWLEDGE BASE:\n" + "\n".join(lines) + "\n"

        system_prompt = (
            "You are a strict JSON-only quiz generation engine for TKRCET. "
            f"\n{kb_part}\n"
            "CRITICAL: Output ONLY a valid JSON array of objects. "
            "NO preamble, NO markdown code fences (```json), NO conversational filler, NO trailing text. "
            "The very first character must be '[' and the very last character must be ']'."
        )

        prompt = (
            f"Generate a {request.difficulty} difficulty quiz about '{request.topic}' "
            f"with exactly {request.num_questions} questions. "
            "Use this EXACT structure content: "
            '[{"question": "What is...?", "options": ["Choice1", "Choice2", "Choice3", "Choice4"], "correctAnswer": 0}]. '
            "Return NOTHING but the JSON array."
        )

        logger.info("[/generate_quiz] Calling Ollama…")
        response = await asyncio.wait_for(
            asyncio.to_thread(
                ollama.chat,
                model='llama3.2:3b',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user',   'content': prompt}
                ],
                options={"temperature": 0.2}   # less random = more JSON-compliant output
            ),
            timeout=180.0
        )
        logger.info("[/generate_quiz] Ollama responded.")

        raw_content = response.message.content
        clean_content = _extract_json_from_llm_response(raw_content)

        try:
            quiz_json = json.loads(clean_content)
            return {"quiz": quiz_json}
        except json.JSONDecodeError:
            logger.error(f"[/generate_quiz] Invalid JSON: {clean_content[:300]}")
            return {"error": "Failed to parse quiz JSON", "raw": clean_content}

    except asyncio.TimeoutError:
        logger.error("[/generate_quiz] Timeout after 180 s")
        raise HTTPException(status_code=504, detail="Quiz generation timed out.")
    except Exception as e:
        logger.error(f"[/generate_quiz] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- User Storage ---
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
        logger.error(f"[/save_user] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/load_user/{fullname}")
async def load_user(fullname: str):
    try:
        filename = f"{fullname.replace(' ', '_').lower()}.json"
        path = os.path.join(USERS_DIR, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[/load_user] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "llama3.2:3b"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
