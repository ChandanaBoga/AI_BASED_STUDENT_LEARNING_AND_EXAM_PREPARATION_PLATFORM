# Btech Box - All-in-One Academic SPA

Welcome to the **Btech Box** application guide. This document provides a comprehensive overview of the application's features, technical architecture, and instructions for setup and usage.

## 🚀 Application Overview
**Btech Box** is a modern Single Page Application (SPA) designed for students of TKR College of Engineering and Technology (TKRCET). It centralizes academic resources, provides an AI-powered study assistant, and offers a streamlined dashboard for managing educational content.

---

## ✨ Key Features

### 📊 1. Academic Dashboard
The central hub of the application, providing quick access to all vital modules:
- **Live System Status**: Real-time indicator of application health.
- **Quick Action Cards**: Fast navigation to Study Materials, AI Quiz, and the Curriculum Hub.
- **Department Overview**: Direct links to explore specific college divisions like CSE, CSM, ECE, etc.

### 🤖 2. Study with AI (Llama 3.2 Powered)
An intelligent chat interface that acts as your personal academic assistant:
- **Interactive Chat**: Ask questions about your curriculum, specific subjects, or general academic queries.
- **Local AI Processing**: Uses a locally hosted **llama3.2:3b** model via Ollama for privacy and speed.
- **Structured Responses**: Provides bolded key terms, bulleted lists, and clickable resource links.

### 📚 3. Curriculum Hub (Syllabus)
Access your latest university syllabus with ease:
- **Branch-wise Filtering**: Select your department (CSE, CSM, CSD, IT, ECE, EEE, CIVIL) to see relevant content.
- **Semester Organization**: View curriculum details organized from Semester 1 through Semester 8.
- **Offline Access**: All syllabus PDFs are stored locally within the application for instant viewing.

### 🔍 4. Global Search
A powerful search bar located in the top navigation that allows you to:
- **Filter Resources**: Instantly find specific semesters or topics.
- **SPA Navigation**: Directly navigate to relevant sections based on your search terms.

---

## 🛠 Technical Architecture

### Frontend
- **Framework**: Single Page Application (SPA) architecture.
- **Styling**: Tailwind CSS with custom glassmorphism effects and dark mode support.
- **Icons**: Material Symbols Outlined.

### Backend
- **API Server**: FastAPI (available on port `8001`).
- **AI Engine**: Ollama running the `llama3.2:3b` model.
- **Storage**: Local asset-based resource management (`assets/resources/R22/`).

---

## ⚙️ Setup and Usage

### Prerequisites
- **Python 3.10+**: For running the backend server.
- **Ollama**: Installed and running with the `llama3.2:3b` model pulled.

### Running the Application
1. **Start the Backend**:
   ```bash
   # Navigate to the project root
   backend\venv\Scripts\python.exe backend\ai_service.py
   ```
2. **Open the Frontend**:
   Simply open [frontend/combined_app.html](file:///c:/Program%20Files/webapp/frontend/combined_app.html) in any modern web browser.

### Using the AI Assistant
- Ensure the backend server is running.
- Navigate to the **"Study with AI"** tab.
- Type your question and interact with the assistant.

---

## 📂 Resource Organization
Syllabus files are systematically organized in:
`frontend/assets/resources/R22/semester_[NUM]/syllabus/`

> [!NOTE]
> All resources have been localized to ensure they open directly from your project folder, providing a seamless experience without external redirects.

---

## 🎯 Tips for Success
- Use the **Global Search** if you're looking for a specific semester's resources quickly.
- Toggle the **Dark Mode** for a more comfortable reading experience at night.
- Keep your **Ollama** service updated for the best AI response performance.

Good luck with your studies! 🎯
