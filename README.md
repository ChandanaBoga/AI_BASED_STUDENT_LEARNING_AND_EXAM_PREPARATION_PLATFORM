# TKR College Engineering Web App (Btech Box)

A comprehensive academic system for TKR College of Engineering and Technology, featuring an AI chatbot, quiz generator, and proctoring service.

## Setup and Installation

### 1. Open Terminal and Navigate to Project
Open PowerShell or Command Prompt as Administrator and run:
```powershell
cd "C:\Program Files\webapp"
```

### 2. Activate Virtual Environment (Optional/Debugging)
To manually enter the environment used by the AI service:
```powershell
# PowerShell
.\backend\venv\Scripts\Activate.ps1

# Command Prompt
backend\venv\Scripts\activate.bat
```

### 3. Install Dependencies
If you need to refresh the packages:
```powershell
pip install -r requirements.txt
```

### 4. Setup AI Models (Ollama)
Ensure **Ollama** is installed and running, then pull the required model:
```powershell
ollama pull llama3.2:3b
```

## How to Run

The easiest way to start all services (Frontend, AI Service, and Proctoring) is to use the `backend.py` script.

1. **Start all services**:
   ```powershell
   python.exe backend.py
   ```
2. **Access the Application**:
   - Open your web browser and navigate to:
     `http://localhost:8080/combined_app.html`

## Service Overview

- **Frontend Server**: http://localhost:8080 (Served via Python's `http.server`)
- **AI Service (FastAPI)**: http://localhost:8001 (Handles Chatbot and Quiz)
- **Proctoring Service**: http://localhost:5050 (Moondream-based distraction analysis)

## Troubleshooting

- **Ollama Connection**: Ensure Ollama is running before starting the services.
- **Python Interpreter**: If using VS Code, ensure the `backend/venv` interpreter is selected for the `ai_service.py` file to avoid import errors.