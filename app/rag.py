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
    
    def rerank_documents(self, query, docs):
        logger.info(f"Reranking {len(docs)} documents...")

        docs_formatted = ""
        for idx, doc in enumerate(docs):
            docs_formatted += f"[{idx}] {doc}\n\n"

        prompt = f"""
        Tugas Anda adalah memilih 3 dokumen yang PALING RELEVAN untuk menjawab pertanyaan berikut.
        Urutkan berdasarkan tingkat relevansinya.

        Pertanyaan: {query}

        Daftar dokumen:
        {docs_formatted}

        Kembalikan HANYA nomor indeks dokumen (contoh: 2, 0, 5) tanpa penjelasan apapun.
        """

        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt
        )

        try:
            selected_indices = [int(i.strip()) for i in response.text.split(',')]
            reranked_docs = [docs[i] for i in selected_indices if i < len(docs)]
            return reranked_docs
        except Exception as e:
            logger.warning(f"Rerank failed: {e}. Falling back to top documents")
            return docs[:3]

    
    def generate_answer(self, query, history=[]):
        logger.info("Generating answer with LLM...")
        debug_info = {}
        standalone_query = self.contextualization_query(query, history)
        debug_info['standalone_query'] = standalone_query

        docs = self.search(standalone_query, k=10)
        debug_info['raw_retrieval'] = docs

        final_docs = self.rerank_documents(standalone_query, docs)
        debug_info['reranked_docs'] = final_docs
        context = "\n\n".join(final_docs)

        conversation = ""
        for h in history[-3:]:
            conversation += f"User: {h['question']}\nAssistant: {h['answer']}\n"
            
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=f"""
            Anda adalah Customer Support BFI Finance yang solutif.
            
            Tugas: Jawab pertanyaan user sesuai dengan informasi di Konteks.
            
            Konteks:
            {context}

            Aturan:
            1. Jika informasi ada di konteks (meskipun tidak eksplisit angka/durasi), jelaskan apa yang ada di konteks tersebut.
            2. Gunakan bahasa yang ramah dan profesional.
            3. Jika benar-benar tidak ada hubungannya sama sekali, barulah katakan Anda tidak tahu.
                     
            Riwayat percakapan:
            {conversation}
   
            Question:
            {query}
            """
        )

        return response.text, debug_info
        
