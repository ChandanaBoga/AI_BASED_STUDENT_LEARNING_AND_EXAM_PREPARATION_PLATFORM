# Btech Box - All-in-One Academic SPA

Welcome to the **Btech Box** application guide. This document provides a comprehensive overview of the application's features, technical architecture, and instructions for setup and usage.

## 🚀 Application Overview
**Btech Box** is a modern Single Page Application (SPA) designed for students of TKR College of Engineering and Technology (TKRCET). It centralizes academic resources, provides an AI-powered study assistant, and offers a streamlined dashboard for managing educational content.

---

## ✨ Key Features

### 📊 1. Academic Dashboard
The central hub of the application, providing quick access to all vital modules:
- **Your Learning Velocity**: An interactive, horizontal glass bar that provides real-time performance summaries (Subjects, Attempts, Avg Score). Clicking the bar expands it into a detailed subject-performance grid.
- **Detailed Subject Cards**: Within the expanded view, each subject is represented by a glassmorphic card showing its best score, attempts count, and an animated accuracy bar.
- **Quick Action Cards**: Fast navigation to Study Materials, AI Quiz, and the Curriculum Hub.
- **Department Overview**: Direct links to explore specific college divisions like CSE, CSM, ECE, etc.

### 🤖 2. Study with AI (Llama 3.2 Powered)
An intelligent chat interface that acts as your personal academic assistant:
- **Interactive Chat**: Ask questions about your curriculum, specific subjects, or general academic queries.
- **AI Quiz Generation**: Effortlessly generate custom quizzes based on any topic of your choice.
- **Real-time Results**: Receive immediate feedback on your performance with automated scoring and an "Average Score" tracking system.
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

### 👤 5. Personalization & Sync
Btech Box provides a persistent experience for authenticated users:
- **User Profiles**: Login to access personalized performance metrics and historical data.
- **Cloud Synchronization**: Your quiz scores and "Learning Velocity" stats are periodically synced with the backend, allowing you to pick up exactly where you left off on any device.

---

## 🛠 Technical Architecture

### Frontend
- **Framework**: Single Page Application (SPA) architecture.
- **Styling**: Vanilla CSS and Tailwind CSS for glassmorphism effects and dark mode.
- **Interactivity**: Dynamic "Learning Velocity" dashboard with animated progress bars and expandable sections.

### Backend
- **API Server**: FastAPI (available on port `8001`).
- **AI Engine**: Ollama running the `llama3.2:3b` model for chat and `moondream:1.8b` for proctoring.
- **Data Persistence**: JSON-based user data storage with automated backend synchronization.

---

## ⚙️ Setup and Usage

### Prerequisites
- **Python 3.10+**: For running the backend server.
- **Ollama**: Installed and running with the `llama3.2:3b` and `moondream:1.8b` models pulled.

### Running the Application
1. **Start the Orchestrator**:
   ```bash
   # Navigate to the project root and run the launcher
   python launcher_app.py
   ```
2. **Access the Portal**:
   Simply open `http://localhost:8001/` in any modern web browser.

### Using the AI Assistant & Quizzes
- Ensure the backend server is running.
- Navigate to **"Study with AI"** or **"AI-Powered Quiz"**.
- For custom quizzes, enter a topic and click "Generate".

---

## 📂 Resource Organization
Syllabus files are systematically organized in:
`frontend/assets/resources/R22/semester_[NUM]/syllabus/`

> [!NOTE]
> All resources have been localized to ensure they open directly from your project folder, providing a seamless experience without external redirects.

---

## 🎯 Tips for Success
- **Verify your progress** regularly using the "Learning Velocity" bar on the dashboard.
- Utilize the **AI Quiz** feature to test yourself on difficult subjects.
- Toggle **Dark Mode** for a more focused experience during late-night study sessions.

Good luck with your studies! 🎯
