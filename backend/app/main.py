import os
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.app.models import (
    BatchGenerationRequest, SingleItemRegenerateRequest, BatchGenerationResponse
)
from backend.app.agent import agent_engine
from backend.app.vectorstore import vector_store_instance

app = FastAPI(
    title="AI Sports Engagement Content Agent API",
    description="Backend API generating grounded, multi-format Instagram sports content (MCQs, True/False, Polls, Fill-in-blanks, Guess-the-number).",
    version="1.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AI Sports Engagement Content Agent",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/meta")
def get_metadata():
    return {
        "sports": ["Cricket", "Football", "Tennis", "Basketball", "Badminton", "Formula 1", "Volleyball"],
        "difficulties": ["Easy", "Medium", "Hard"],
        "formats": ["Mixed Batch", "MCQ", "True / False", "This-or-That Poll", "Fill in the Blank", "Guess the Number"],
        "vectorstore_status": "Ready" if vector_store_instance.collection else "Fallback Mode"
    }

@app.post("/api/generate-batch")
def generate_batch(request: BatchGenerationRequest):
    try:
        items = agent_engine.generate_batch(request)
        return {
            "sport": request.sport,
            "difficulty": request.difficulty,
            "content_format": request.content_format,
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/regenerate-item")
def regenerate_item(request: SingleItemRegenerateRequest):
    try:
        # Create a 1-item batch request for targeted format
        single_req = BatchGenerationRequest(
            sport=request.sport,
            difficulty=request.difficulty,
            content_format=request.content_format,
            count=1,
            use_web_search=request.use_web_search
        )
        new_items = agent_engine.generate_batch(single_req)
        if new_items:
            new_item = new_items[0]
            new_item["id"] = request.target_item_id or f"item_{uuid.uuid4().hex[:8]}"
            return {"item": new_item}
        raise HTTPException(status_code=500, detail="Failed to regenerate item")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
