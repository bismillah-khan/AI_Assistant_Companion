

# AI Assistant Companion

## 📖 Project Description

**AI Assistant Companion** is a Voice & Text Command AI Agent System designed for real-world automation and intelligent reasoning.  
- **Who is it for?**  
  Individuals, developers, or teams who want an open-source, extensible AI assistant for automating tasks, answering queries, and enabling intelligent conversational interfaces.  
- **Core Purpose:**  
  Enable both voice and text-based user interaction with advanced AI models, supporting automation, Q&A, and reasoning.  
- **Key Capabilities:**  
  - Natural conversation via voice or text  
  - Real-world automation hooks  
  - Intelligent reasoning using modern LLMs  
  - Easily extensible via plugins

---

## 🧠 Features

- Voice and text command interface
- Real-world task automation
- Intelligent reasoning with open-source LLMs
- Extensible via plugin system
- Multi-modal IO (voice, text, TTS)

---

## 🛠 Technologies Used

### Frontend
- (Specify if React, Vue, Next.js, etc.)
- (Example: React)
- (Styling: Tailwind CSS, Material UI)
- (Networking: Axios or fetch)

### Backend
- **Language:** Python
- **Framework:** (e.g., FastAPI, Flask)  
- **LLM API:** Groq API (supports Llama 3, Mixtral, Gemma2)
- **Vector Database:** FAISS
- **Speech-to-Text:** Whisper
- **Text-to-Speech:** OpenAI TTS

### AI & ML
- Open-source LLMs (Llama, Mixtral, Gemma2, etc.)
- Embedding Model: all-MiniLM-L6-v2
- Vector database: FAISS

---

## 💻 Installation Guide

### Backend Setup

```bash
git clone <repo>
cd backend
python -m venv venv
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

---

## ⚙️ Environment Variables

All secrets/parameters are managed via `.env` files.  
Create a `.env` (see `.env.example`) file with the following keys:

```env
APP_NAME="AI Agent Backend"
MONGO_URI="mongodb://localhost:27017"
LLM_API_BASE="https://api.groq.com"
LLM_API_KEY=""
LLM_MODEL="llama-3.3-70b-versatile"
TTS_API_KEY=""
...
```
**See** [.env.example](https://github.com/bismillah-khan/AI_Assistant_Companion/blob/main/.env.example) for the full set.  
**Backend:** Place .env inside `backend/` and populate required API secrets (Groq, TTS).

---

## 🗂 Project Structure

```
AI_Assistant_Companion/
│
├── backend/
├── frontend/
├── infra/
├── .env.example
├── GROQ_SETUP.md
├── README.md
└── .gitignore
```

---

## 🚀 Future Improvements

- Add authentication support
- Add analytics/dashboard
- Multi-user support
- Voice assistant improvements
- UI/UX animations
- Cloud deployment
- Further response optimization

---

## 🤝 Contribution Guide

1. **Fork** the repository to your GitHub.
2. **Create a branch** (`feature/my-feature`).
3. **Make changes** and commit with descriptive messages.
4. **Push** to your fork and submit a **pull request (PR)**.
5. **Coding standards:** Clean code, follow PEP8 (for Python), industry best practices.

### Rules

- Do **NOT** break working features.
- Do **NOT** remove necessary dependencies/files.
- Keep code clean and well-commented.
- Ensure project runs successfully after your changes.

---

*For any questions or support, please open an issue in the repository.*

---

Let me know if you'd like me to update this file in your repo or if you want to adjust any section!
