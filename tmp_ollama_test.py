import ollama
import os

# Try to match the environment from launcher_app.py
os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"

try:
    print("Connecting to Ollama...")
    models = ollama.list()
    print("Response structure:", type(models))
    print("Models:", models)
    print("SUCCESS: Connected to Ollama.")
except Exception as e:
    import traceback
    print(f"FAILURE: Could not connect to Ollama.")
    traceback.print_exc()
