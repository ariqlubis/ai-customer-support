# AI Customer Support

An AI-powered Customer Support Copilot built with a Retrieval-Augmented Generation (RAG) architecture. This system is designed to automatically answer Frequently Asked Questions (FAQ) with high accuracy using Google Generative AI and vector search.

![Architecture Diagram](assets/Blank%20diagram%20-%20Page%201.svg)

## Features

- **Contextual AI Chatbot:** Uses Google Gemini (Generative AI) to provide helpful and friendly customer support.
- **RAG System (Retrieval-Augmented Generation):** Retrieves relevant documents from a vector database before answering to prevent hallucinations.
- **Standalone Question Generator:** Converts follow-up questions from chat history into clear, standalone queries.
- **Document Re-ranking:** Re-ranks the retrieved documents to provide the most relevant context to the AI.
- **Modern User Interface:** Built with Streamlit for a clean, chat-like experience.
- **Trace Thought Process:** Users can see how the AI retrieved and selected information.
- **FastAPI Backend:** A lightweight and fast API for chat interactions.
- **Vector Database support:** Integrates with Qdrant (local and cloud) and FAISS.
- **Dockerized:** Easy deployment using Docker and Docker Compose.

## Project Structure

- `app/` : Contains the FastAPI backend and RAG logic.
  - `main.py` : FastAPI server endpoints.
  - `rag.py` : RAG system implementation.
  - `embedding.py` : Logic to generate embeddings.
- `ui/` : Contains the Streamlit frontend.
  - `streamlit_app.py` : Frontend application.
- `pipeline/` : ETL pipeline scripts.
  - `ingest.py` : Script to process raw FAQ data, generate vector embeddings, and save them.
- `docker-compose.yml` : Configuration for Qdrant and PostgreSQL local databases.
- `Dockerfile` : Blueprint for building the backend Docker image.

## Setup Instructions

### 1. Prerequisites
- Python 3.11 or newer
- Docker and Docker Compose (optional, for running local databases)
- Google Gemini API Key

### 2. Environment Variables
Create a `.env` file in the root folder with the following variables:
```env
# Google AI API Key
GOOGLE_API_KEY="your_google_api_key_here"

# Qdrant Vector DB Settings
QDRANT_HOST="localhost" # Or your Qdrant cloud URL
QDRANT_PORT="6333"
# QDRANT_API_KEY="" # Add this if you use Qdrant Cloud

# Backend Settings
BACKEND_URL="http://127.0.0.1:8000"
```

### 3. Installation
Install the required Python packages:
```bash
pip install -r requirements.txt
```
*Tip: If you use the `uv` package manager, you can run `uv pip install -r requirements.txt`.*

### 4. Run Vector Database (Local Qdrant)
If you want to use a local Qdrant database, you can start it using Docker Compose:
```bash
docker-compose up -d qdrant_db
```

### 5. Data Ingestion
Run the pipeline to generate embeddings from your data and save them:
```bash
python pipeline/ingest.py
```

### 6. Run the Application
You need to open two terminal windows to run both the backend and the frontend at the same time.

**Terminal 1 (FastAPI Backend):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 (Streamlit UI):**
```bash
streamlit run ui/streamlit_app.py
```

## How It Works

1. **User Query:** The user asks a question in the Streamlit web interface.
2. **Contextualization:** The system looks at the chat history and makes the new question clear on its own (a standalone query).
3. **Retrieval:** The system searches the Qdrant vector database to find documents related to the question.
4. **Re-ranking:** It re-ranks the documents and picks the top 3 most relevant ones.
5. **Generation:** Google Generative AI reads the selected documents and generates a friendly, accurate response based on the "Multifinance" context.
6. **Output:** The answer is sent back to the user, along with debug information (visible if you click "Trace AI Thought Process").

## Technologies Used
- **Backend Framework:** FastAPI, Python
- **Frontend Framework:** Streamlit
- **AI/LLM:** Google Generative AI (Gemini)
- **Vector Database:** Qdrant, FAISS
- **Containerization:** Docker
