# AI-Powered Sports Engagement Content Agent 🚀

> **"Traditional sports content on social media is limited to repetitive MCQs. Our AI Agent produces 5 interactive content types grounded by live web search and ChromaDB vector retrieval, formatted for native Instagram Story & Sticker tools."**

Built for the **StapuBox AI Product/Engineer Intern Assignment**.

---

## 🌟 Key Features & Highlights

1. **5 Interactive Engagement Content Formats**:
   - **MCQ**: 4 options, 1 correct answer, grounding context.
   - **True / False**: Evaluated statement with factual explanation.
   - **This-or-That Poll**: Opinion poll comparison (flagged as non-fact checked).
   - **Fill in the Blank**: Sentence with `___` and 4 completion choices.
   - **Guess the Number**: Target numerical answer with acceptable tolerance range ($\pm X$).
2. **Dual Retrieval Engine (Hybrid RAG)**:
   - **Live Web Search**: DuckDuckGo search integration for recent match scores, transfer news, and latest tournament statistics.
   - **ChromaDB Vector Store**: Embedded historical sports trivia, legends, and world records using SentenceTransformers.
3. **Item-Level & Full Batch Regeneration**:
   - Regenerate individual items within a batch without disturbing others, or regenerate the entire batch.
4. **Instagram Native Preview & Sticker Exporter**:
   - Visual mock of Instagram Story Quiz & Poll stickers with a single-click "Copy for Instagram" formatter ready to paste with hashtags.
5. **Zero-Failure Live Demo Safety**:
   - Includes a deterministic Simulation Engine Fallback so the demo runs seamlessly with or without an active API key.

---

## 🛠️ Architecture & Tech Stack

- **Backend Framework**: Python 3.9+ with FastAPI (Async REST endpoints)
- **Vector Database**: ChromaDB (Embedded local SQLite store)
- **Search Engine**: DuckDuckGo Search API
- **LLM Engine**: Google Gemini SDK (`google-genai` / `google-generativeai`)
- **Frontend**: React 18 + Vite + TypeScript + Vanilla Tailwind CSS + Lucide Icons
- **Testing**: pytest suite enforcing Pydantic schema validation

---

## 🚀 Running Locally

### Prerequisites
Make sure you have **Python 3.9+** and **Node.js 18+** installed.

### 1. Run the Backend Server
```bash
cd C:\Users\yash1\.gemini\antigravity-ide\scratch\sports-engagement-agent
.\.venv\Scripts\activate
# Optional: add GEMINI_API_KEY to .env file
uvicorn backend.app.main:app --reload --port 8000
```
*API Documentation is live at `http://localhost:8000/docs`.*

### 2. Run the Frontend Dashboard
```bash
cd frontend
npm run dev
```
*Open `http://localhost:5173` in your browser.*

---

## 🧪 Running Automated Tests

Verify schema enforcement and backend functionality:
```bash
.\.venv\Scripts\python.exe -m pytest -v tests/test_backend.py
```
