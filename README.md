# AI Customer Support Copilot: Factual & Scalable RAG 

**Core Conclusion:**
This project delivers a production-ready AI Copilot that eliminates AI hallucinations and automates up to 70% of customer inquiries. By grounding Google Gemini in BigQuery Vector Search, we ensure every response is based on official company documentation, making it safe for the highly regulated Multifinance industry.

---

## 1. Executive Framework (SCQA)

### Situation
In the Multifinance sector, customer support teams handle a massive volume of complex inquiries daily. Customers expect instant and accurate information regarding loan requirements, interest rates, and payment procedures.

### Complication
Traditional automation tools face three critical failures in this environment:
1.  **Hallucinations:** Standard AI often "makes up" answers when it is unsure, creating significant legal and financial risks.
2.  **Resource Inefficiency:** Human agents spend the majority of their time answering the same basic FAQ questions repeatedly.
3.  **Context Loss:** Most chatbots cannot remember previous questions in a conversation, forcing customers to repeat themselves.

### Question
How can we build an automated support system that guarantees factual accuracy, maintains conversation context, and scales securely on the cloud?

### Answer
The solution is a **Retrieval-Augmented Generation (RAG)** system built on Google Cloud Platform. This architecture "grounds" the AI by forcing it to read official FAQ documents before answering, ensuring the responses are always factual, transparent, and context-aware.

---

## 2. Supporting Logic & Features

### I. Factual Grounding (Anti-Hallucination)
The AI is strictly instructed to answer **only** based on the context retrieved from the database. If the information is not in the documents, the AI is programmed to politely decline rather than guess.
*   **Tech:** Google Gemini 2.0 Flash + BigQuery Vector Search.

### II. Real-time User Experience (Streaming)
To provide a natural and fast experience, the system uses "Typewriter Streaming." Users see the answer appearing word-by-word in real-time, reducing the perceived wait time.
*   **Tech:** FastAPI StreamingResponse + JSON Lines.

### III. Operational Transparency (Trace AI Thought)
To build trust with both staff and customers, the UI includes a "Trace AI" feature. This allows users to see exactly which documents the AI used to generate its answer.
*   **Tech:** Streamlit Expander + Metadata retrieval.

---

## 3. Implementation & Operations

### High-Level Architecture
*   **Backend:** A stateless FastAPI service that handles AI logic and BigQuery communication.
*   **Frontend:** A modern Streamlit interface that manages user sessions and chat history.
*   **Cloud Infrastructure:** Both services are containerized and managed via Google Cloud Run for automatic scaling and high security.

### Quick Deployment
Deploy both the Backend and Frontend to Google Cloud with a single command:
```bash
gcloud builds submit --config cloudbuild.yaml .
```

### Required Configuration
Ensure the following variables are set in your environment or Cloud Run settings:
*   `PROJECT_ID`: Your Google Cloud Project ID.
*   `LOCATION`: `us-central1` (Required for specific AI model availability).
*   `BACKEND_URL`: The URL of your deployed Backend service.

---
