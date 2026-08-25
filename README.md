# AI-Powered Sports Engagement Content Agent 🏆

> Built for StapuBox AI Product/Engineer Intern Assignment

Generate Instagram-ready sports quizzes, polls, and challenges 
powered by Hybrid RAG (ChromaDB + Live Web Search) and Google Gemini.

## Architecture

```
User Input (Sport + Difficulty + Content Type)
                       ↓
               Hybrid RAG Router
               ↙               ↘
        ChromaDB          DuckDuckGo Web Search
   (Historical facts)     (Recent news/results)
               ↘               ↙
          Context Merger + Sport Filter
                       ↓
         Type-Specific Prompt Template
      ┌─────────────────────────────┐
      │ MCQ / True-False / Poll /   │
      │ Fill-in-Blank / Guess-Num   │
      └─────────────────────────────┘
                       ↓
              Google Gemini LLM
                       ↓
          Pydantic Schema Validation
           (auto-retry on failure)
                       ↓
               Duplicate Checker
          (session dedup via difflib)
                       ↓
          Instagram-Formatted Output
           (Copy for Story/Feed/Reel)
```

## Features
- 5 content types: MCQ, True/False, This-or-That Poll, Fill-in-Blank, Guess-the-Number
- Batch of 4-5 items per request, each with different query angle
- Per-item regeneration without disturbing rest of batch
- Sport-locked generation (no cross-sport contamination)
- Source citation on every card (ChromaDB vs Web Search)
- Instagram copy formatter with hashtags

## Type-Specific Architecture

Each content type has its own prompt template with different rules:

| Type | Blank/Options Rule | Source Priority |
|------|-------------------|-----------------|
| MCQ | 4 specific options, 1 correct | Web Search first |
| True/False | Single checkable fact statement | ChromaDB first |
| This-or-That | 2 options, no correct answer, opinion | No fact-check |
| Fill-in-Blank | Blank = number/name/year/place ONLY | ChromaDB first |
| Guess-the-Number | Exact numeric target + tolerance | Web Search first |

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Gemini API key (free at aistudio.google.com)

### 1. Clone & Install Backend
```bash
git clone https://github.com/YashAsija/Sports_Engagement_AI_Agent
cd Sports_Engagement_AI_Agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Seed ChromaDB
```bash
python seed_db.py
```

### 4. Run Backend
```bash
uvicorn backend.app.main:app --reload --port 8000
# API docs at http://localhost:8000/docs
```

### 5. Run Frontend
```bash
cd frontend
npm install
npm run dev
# App at http://localhost:5173
```

## Environment Variables

```env
GEMINI_API_KEY=your_gemini_key_here
CHROMA_PERSIST_DIR=./chroma_db
```

## Running Tests
```bash
pytest -v tests/test_backend.py
```

## Project Structure

```
Sports_Engagement_AI_Agent/
├── backend/
│   └── app/
│       ├── main.py        # FastAPI entry point
│       ├── generator.py   # LLM generation + batch logic
│       ├── retriever.py   # ChromaDB + web search
│       ├── validator.py   # Pydantic schemas per type
│       └── templates/     # Type-specific prompt templates
├── frontend/
│   └── src/               # React + TypeScript dashboard
├── tests/
│   └── test_backend.py    # Schema validation tests
├── seed_db.py             # Populate ChromaDB with sports facts
├── requirements.txt
└── .env.example
```
