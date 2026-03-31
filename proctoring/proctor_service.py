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
    "Analyze this webcam image for a proctoring system. "
    "Is the student distracted or looking away (yes/no)? "
    "Is there any other person in the frame (yes/no)? "
    "Respond exactly in this format: "
    "IS_DISTRACTED: [YES/NO] | MULTIPLE_PEOPLE: [YES/NO]"
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
        # Save a debug frame to see what AI sees
        debug_dir = os.path.join(os.path.dirname(__file__), "debug_frames")
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        image.save(os.path.join(debug_dir, "last_frame.jpg"))

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
        
        raw_answer = response.message.content if response.message else ""
        answer = raw_answer.strip().lower()
        
        log.info(f"[Proctor] Raw AI Response: '{raw_answer}'")

        # Robust Boolean Detection
        is_distracted = "is_distracted: yes" in answer or "distracted: yes" in answer
        is_multi_person = "multiple_people: yes" in answer or "multiple: yes" in answer or "people: yes" in answer

        # Fail-Safe: If coordinates (e.g. [0.1, 0.2]) are returned, it likely found someone
        if not is_multi_person and ("[" in raw_answer and "]" in raw_answer):
            log.warning("[Proctor] Detected coordinates in response. Flagging as Multi-Person presence.")
            is_multi_person = True

        # Fallback for simple "yes"
        if not is_distracted and not is_multi_person:
            if answer == "yes": is_distracted = True

        log.info(f"[Proctor] Final Decision -> Distracted: {is_distracted} | Multi-Person: {is_multi_person}")
        
        return {
            "is_distracted": is_distracted,
            "is_multi_person": is_multi_person,
            "description": raw_answer[:255]
        }

    except Exception as exc:
        log.error(f"Ollama Moondream inference failed: {exc}")
        return {"is_distracted": False, "is_multi_person": False, "description": f"error: {exc}"}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    """Verify that the proctoring service and its models are ready."""
    try:
        # Check if the required model is pulled
        models_info = ollama.list()
        models = getattr(models_info, 'models', []) or []
        available_models = [m.model for m in models if m.model]
        
        model_ready = any(MODEL_NAME in m for m in available_models)
        
        if not model_ready:
            log.warning(f"Health check failed: Model {MODEL_NAME} not found")
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
    return jsonify(result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PROCTOR_PORT", 5050))
    print(f"[Proctor] Starting Production Server on http://127.0.0.1:{port} (Ollama Mode)")
    # Using waitress for production-ready serving on Windows
    serve(app, host="0.0.0.0", port=port)
