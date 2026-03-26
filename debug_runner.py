import traceback
import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

print("Debug runner starting...")
try:
    print("Importing app...")
    from backend.ai_service import app
    import uvicorn
    print("Starting uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
except Exception:
    print("CRASH DETECTED! Writing to crash_debug.log")
    with open("crash_debug.log", "w") as f:
        traceback.print_exc(file=f)
    traceback.print_exc()
    sys.exit(1)
except SystemExit as e:
    print(f"SystemExit detected with code: {e.code}")
    with open("crash_debug.log", "a") as f:
        f.write(f"\nSystemExit: {e.code}\n")
    sys.exit(e.code)
