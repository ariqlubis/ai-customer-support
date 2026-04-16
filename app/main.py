from fastapi import FastAPI
from .rag import RAGSystem
from .logger import get_logger

logger = get_logger()
app = FastAPI()

rag = None  
chat_history = []

def get_rag():
    """Lazy initialization - hanya buat RAGSystem saat pertama kali dibutuhkan"""
    global rag
    if rag is None:
        logger.info("Initializing RAG system...")
        rag = RAGSystem()
    return rag

@app.get("/")
def health_check():
    """Health check endpoint agar Cloud Run tahu container sudah siap"""
    return {"status": "ok"}

@app.get("/chat")
def chat(query: str):
    logger.info(f"Incoming query: {query}")

    global chat_history

    try:
        result = get_rag().generate_answer(query, chat_history)  # <-- Panggil get_rag()
        chat_history.append({
            "question": query,
            "answer": result
        })

        if len(chat_history) > 10:
            chat_history.pop(0)

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": "Something went wrong"}

    logger.info(f"Response generated")
    return {
        "query": query,
        "answer": result
    }
