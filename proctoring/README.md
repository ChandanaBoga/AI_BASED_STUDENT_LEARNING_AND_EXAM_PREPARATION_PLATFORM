# 🎓 Quiz Proctoring Module

Uses **Moondream vision LLM** to monitor students during quizzes via their webcam.

## Folder structure

```
webapp/proctoring/
├── proctor_service.py   # Flask backend – runs Moondream on webcam frames
├── proctor_client.js    # Browser client – captures frames, shows warnings
├── proctor_ui.css       # Styles for the warning popup & webcam PiP
├── start_proctor.py     # One-click launcher (installs deps + starts service)
└── requirements.txt     # Python dependencies
```

## How it works

1. When a student navigates to **Study with AI**, the browser asks for webcam permission.
2. Every **7 seconds** a frame is captured and sent (base64 JPEG) to the local backend.
3. Moondream answers: *"Is this person distracted?"*
4. If **yes** → a warning popup appears showing remaining chances (●●●●●).
5. After **5 warnings** → the quiz resets to Semester 1.

## Quick start

```bash
# From the webapp/proctoring/ folder:
python start_proctor.py
```

The service runs on **http://localhost:5050**.  
Keep this terminal open while students use the quiz.

## Requirements

- Python 3.9+
- Webcam on the student's device
- The proctoring service running locally

## First run note

`moondream` will download the model weights (~1.7 GB) on first launch. Subsequent starts are instant.

## Endpoints

| Method | Path       | Description                          |
|--------|-----------|--------------------------------------|
| GET    | /health   | Check if service is running          |
| POST   | /analyze  | Analyze a base64 JPEG frame          |

### POST /analyze – request body
```json
{ "image": "<base64-encoded JPEG>" }
```

### Response
```json
{ "is_distracted": true, "description": "yes" }
```
