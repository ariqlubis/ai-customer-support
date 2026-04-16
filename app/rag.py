import json
import numpy as np
import faiss
from .embedding import get_embedding, get_embedding_batch
from .config import TOP_K, GENERATION_MODEL, client
from .logger import get_logger

logger = get_logger()

class RAGSystem:
    def __init__(self, data_path: str="data/faq.json"):
        self.texts = []
        self.metadata = []
        self.index = None
        self.load_data(data_path)

    def load_data(self, data_path: str):
        logger.info("Loading data...")
        with open(data_path, 'r') as f:
            data = json.load(f)

        for i in data:
            text = f"Q: {i['question']}\nA: {i['answer']}"
            self.texts.append(text)
            self.metadata.append(i)
        
        logger.info(f"Total documents: {len(self.texts)}")
        embeddings = get_embedding_batch(self.texts)
        embeddings = np.array(embeddings)

        self.index = faiss.IndexFlatL2(len(embeddings[0]))
        self.index.add(embeddings)

    def search(self, query, k=TOP_K):
        logger.info(f"Searching for query: {query}")
        q_emb = np.array([get_embedding(query)])
        distances, indices = self.index.search(q_emb, k)

        return [self.texts[i] for i in indices[0]]

    def contextualization_query(self, query, history=[]):
        if not history:
            return query

        history_str = ""
        for h in history[-3:]:
            history_str += f"User: {h['question']}\nAI: {h['answer']}\n"
        
        prompt = f"""
        Berdasarkan riwayat percakapan berikut, ubah pertanyaan terakhir menjadi
        pertanyaan mandiri yang bisa dipahammi tanpa melihat riwayat.
        JANGAN menjawab pertanyaannya, cukup kembalikan pertanyaan yang sudah diperbaiki.

        Chat history:
        {history_str}

        Pertanyaan terakhir: {query}
        Standalone Question:
        """

        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt
        )

        contextualization_query = response.text.strip()
        logger.info(f"Original Query: {query}")
        logger.info(f"Contextualization Query: {contextualization_query}")

        return contextualization_query
    
    def generate_answer(self, query, history=[]):
        logger.info("Generating answer with LLM...")
        standalone_query = self.contextualization_query(query, history)
        docs = self.search(standalone_query)
        context = "\n\n".join(docs)

        conversation = ""
        for h in history[-3:]:
            conversation += f"User: {h['question']}\nAssistant: {h['answer']}\n"
            
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=f"""
            Anda adalah customer support BFI Finance.
            Jawab hanya berdasarkan konteks berikut.
            Jika tidak ada jawaban, katakan tidak tahu.
                     
            Context:
            {context}

            Riwayat percakapan:
            {conversation}
   
            Question:
            {query}
            """
        )
        return response.text
        
