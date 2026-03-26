import base64
import io
import logging
import sys
import os
import asyncio

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

from typing import Optional, Any
from waitress import serve
import ollama

# ---------------------------------------------------------------------------
# Ollama / Moondream config
# ---------------------------------------------------------------------------
MODEL_NAME = "moondream:1.8b"

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s %(message)s")
log = logging.getLogger("proctor")

DISTRACTION_PROMPT = (
    "Analyze this webcam image carefully. "
    "Is the person's face oriented towards the screen? "
    "Are they looking away, looking at their lap, or looking significantly to the side? "
    "If they are clearly focused on the screen, answer 'no'. "
    "If they are looking away, using a phone, talking, or clearly inattentive, answer 'yes'. "
    "Answer with ONLY one word: 'yes' or 'no'."
)


def decode_image(b64_string: str) -> Image.Image:
    """Decode a base64-encoded image safely."""
    try:
        if "," in b64_string:
            b64_string = b64_string.split(",", 1)[1]
        raw = base64.b64decode(b64_string)
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as e:
        log.error(f"Image decode failed: {e}")
        raise ValueError(f"Malformed image data: {e}")


def analyze_frame(image: Image.Image) -> dict:
    """Run Moondream via Ollama on a single frame and return structured result."""
    try:
        # Convert PIL image to bytes for Ollama
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        # Call Ollama synchronously (waitress threads will handle concurrent requests)
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    'role': 'user',
                    'content': DISTRACTION_PROMPT,
                    'images': [img_bytes]
                }
            ]
        )
        
        raw_answer = response.message.content or ""
        answer = raw_answer.strip().lower()
        
        # Logic: Simple yes/no detection
        is_distracted = "yes" in answer and "no" not in answer
        
        log.info(f"[Proctor] Ollama Raw: '{raw_answer}' | Distracted: {is_distracted}")
        
        return {
            "is_distracted": is_distracted,
            "description": answer[:100]
        }

    except Exception as exc:
        log.error(f"Ollama Moondream inference failed: {exc}")
        return {"is_distracted": False, "description": f"error: {exc}"}



# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    """Verify that the proctoring service and its models are ready."""
    try:
        # Check if the required model is pulled
        models_info = ollama.list()
        available_models = [m.model for m in models_info.models] if hasattr(models_info, 'models') else []
        
        # If the above fails to get names, try a simpler check if possible
        # or just assume it's there if list() didn't raise
        
        model_ready = any(MODEL_NAME in m for m in available_models)
        
        if not model_ready:
            log.warning(f"Health check failed: Model {MODEL_NAME} not found in {available_models}")
            return jsonify({
                "status": "error", 
                "message": f"Model {MODEL_NAME} not found. Please run 'ollama pull {MODEL_NAME}'",
                "engine": "ollama"
            }), 503

        return jsonify({
            "status": "ok", 
            "engine": "ollama", 
            "model": MODEL_NAME,
            "ready": True
        })
    except Exception as e:
        log.error(f"Health check exception: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)
    if not data or "image" not in data:
        return jsonify({"error": "Missing 'image' field in JSON body."}), 400

    try:
        image = decode_image(data["image"])
    except Exception as exc:
        return jsonify({"error": f"Invalid image data: {exc}"}), 400

    result = analyze_frame(image)
    log.info("Analysis result: %s", result)
    return jsonify(result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PROCTOR_PORT", 5050))
    print(f"[Proctor] Starting Production Server on http://localhost:{port} (Ollama Mode)")
    # Using waitress for production-ready serving on Windows
    serve(app, host="0.0.0.0", port=port)
