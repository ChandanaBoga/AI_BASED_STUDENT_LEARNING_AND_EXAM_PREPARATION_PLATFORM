"""
launcher_app.py
---------------
The primary orchestrator for the TKR College Engineering Web App.
Starts all services with a single command:
  python launcher_app.py

Services:
  1. Main App (FastAPI)     -> http://localhost:8001/
  2. Proctor service (AI)    -> http://localhost:5050 (Proxied)
"""

import os
import subprocess
import sys
import time

# Configuration
AI_VENV_PYTHON = os.path.join("backend", "venv", "Scripts", "python.exe")
AI_SCRIPT      = "ai_service.py"
AI_PORT        = 8001

PROCTOR_VENV   = os.path.join("proctoring", "venv", "Scripts", "python.exe")
PROCTOR_SCRIPT = "proctor_service.py"
PROCTOR_PORT   = 5050

def main():
    print("=" * 60)
    print("  TKR COLLEGE ACADEMIC SYSTEM - STARTING SERVICES")
    print("  Press Ctrl+C to stop all servers")
    print("=" * 60)

    # 1. Start Proctoring Service
    print(f"[*] Starting Proctor service on port {PROCTOR_PORT}...")
    proctor_process = None
    if os.path.exists(PROCTOR_VENV):
        proctor_process = subprocess.Popen(
            [PROCTOR_VENV, PROCTOR_SCRIPT],
            cwd="proctoring"
        )
    else:
        print(f"[!] Proctor Venv not found at {PROCTOR_VENV} - skipping.")

    # 2. Start AI Service
    print(f"[*] Starting AI Service on port {AI_PORT}...")
    ai_process = None
    if os.path.exists(AI_VENV_PYTHON):
        ai_process = subprocess.Popen(
            [AI_VENV_PYTHON, AI_SCRIPT],
            cwd="backend"
        )
    else:
        print(f"[!] AI Venv not found at {AI_VENV_PYTHON} - checking for global python...")
        ai_process = subprocess.Popen(
            [sys.executable, AI_SCRIPT],
            cwd="backend"
        )

    print(f"\n[*] Main Application  -> http://localhost:{AI_PORT}")
    print(f"[*] Proctoring Service -> http://localhost:{PROCTOR_PORT}")
    print("[!] Press Ctrl+C to stop both services\n")

    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            if proctor_process and proctor_process.poll() is not None:
                print("[!] Proctoring service stopped unexpectedly.")
            if ai_process and ai_process.poll() is not None:
                print("[!] AI service stopped unexpectedly.")
    except KeyboardInterrupt:
        print("\n[!] Stopping services...")
    finally:
        if proctor_process:
            proctor_process.terminate()
        if ai_process:
            ai_process.terminate()
        print("[*] All services stopped.")

if __name__ == "__main__":
    main()
