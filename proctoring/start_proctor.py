"""
start_proctor.py
================
Helper script to install dependencies and launch the proctoring service.
Run from the webapp/proctoring/ directory:

    python start_proctor.py
"""
import subprocess
import sys
import os

def install_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    print("[Setup] Installing proctoring dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])

def main():
    install_requirements()
    # Launch the service
    service_path = os.path.join(os.path.dirname(__file__), "proctor_service.py")
    print("[Setup] Starting Moondream Proctor Service on http://localhost:5050 ...")
    os.execv(sys.executable, [sys.executable, service_path])

if __name__ == "__main__":
    main()
