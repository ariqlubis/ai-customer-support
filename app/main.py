from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
from pydantic import BaseModel
from typing import List, Optional
from .rag import RAGSystem
from .logger import get_logger

logger = get_logger()
app = FastAPI()

rag = None  

def get_rag():
    global rag
    if rag is None:
        logger.info("Initializing RAG system...")
        rag = RAGSystem()
    return rag

class ChatMessage(BaseModel):
    question: str
    answer: str

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[ChatMessage]] = []

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest):
    logger.info(f"Incoming query: {request.query}")

    try:
        formatted_history = [{"question": h.question, "answer": h.answer} for h in request.history]
        stream, debug = get_rag().generate_answer(request.query, formatted_history)  

        def event_generator():
            yield json.dumps({"type": "debug", "data": debug}) + "\n"
            for chunk in stream:
                if chunk.text:
                    yield json.dumps({"type": "chunk", "content": chunk.text}) + "\n"

        logger.info(f"Streaming response started")
        return StreamingResponse(event_generator(), media_type="application/x-ndjson")

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}
        return {"error": "Something went wrong"}


