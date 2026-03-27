# TKR College Engineering Web App (Btech Box)

A comprehensive academic system for TKR College of Engineering and Technology, featuring an AI chatbot, quiz generator, and proctoring service.

## GitHub Repository
The official codebase is now hosted at:
`https://github.com/ChandanaBoga/AI_BASED_STUDENT_LEARNING_AND_EXAM_PREPARATION_PLATFORM.git`

## Key Improvements
- **AI Quiz Generation**: Robust regex-based parsing ensures valid JSON extraction, resolving previous formatting errors.
- **Chatbot Accuracy**: Expanded knowledge base context and department-specific trigger keywords (e.g., HOD of AIML) for highly accurate responses.
- **Integrated Proctoring**: Moondream-based distraction analysis for secure academic assessments.

## Setup and Installation

### 1. Project Directory
Open PowerShell or Command Prompt as Administrator and run:
```powershell
cd "C:\Program Files\webapp"
```

### 2. Setup AI Models
Ensure **Ollama** is installed and running, then pull the required models:
```powershell
ollama pull llama3.2:3b
ollama pull moondream:1.8b
```

### 3. Run the Application
The primary orchestrator for all services (Foreground, AI, and Proctoring) is `launcher_app.py`:
```powershell
python launcher_app.py
```

## Service Overview
- **Main Portal**: `http://localhost:8001/` (Handles AI Chatbot and Quiz)
- **Proctoring Engine**: `http://localhost:5050` (Active during AI Quiz)
- **Asset Portability**: All resources are version-controlled, including the `data/` knowledge base and `scripts/` utility folder.

## Troubleshooting
- **Ollama Status**: The AI service requires Ollama to be active. Verification can be done by running `ollama list`.
- **Environment**: If errors occur, ensure dependencies are installed via `pip install -r requirements.txt`.