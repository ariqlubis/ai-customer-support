import os
from .embedding import get_embedding
from .config import settings, client
from .logger import get_logger
from google.cloud import bigquery
from google.genai.types import GenerateContentConfig

logger = get_logger()

SYSTEM_INSTRUCTION = """
Anda adalah AI Customer Support Assistant yang ramah, profesional, dan sangat
membantu.
Tugas utama Anda adalah menjawab pertanyaan pelanggan DENGAN TEGAS berdasarkan
KONTEKS yang diberikan.

ATURAN PENTING:
1. Jawab HANYA berdasarkan informasi yang ada di dalam KONTEKS.
2. Jika informasi untuk menjawab pertanyaan TIDAK ADA di dalam KONTEKS,
Anda HARUS menolak dengan sopan. Katakan bahwa Anda tidak memiliki informasi tersebut
atau sarankan untuk menghubungi tim support. Jangan pernah menebak atau mengarang jawaban (halusinasi).
3. Gunakan bahasa yang mudah dipahami dan gunakan emoji secukupnnya agar terlihat ramah.
"""

class RAGSystem:
    def __init__(self):
        self.bq_client = bigquery.Client(project=settings.PROJECT_ID)
        self.table_id = f"{settings.PROJECT_ID}.faq_data.faqs"

    def search(self, query, k=settings.TOP_K):
        query_embedding = get_embedding(query)
        sql = f"""
        SELECT base.question, base.answer, base.category, distance
        FROM VECTOR_SEARCH(
            TABLE `{self.table_id}`,
            'embedding',
            (SELECT {query_embedding} AS query_embedding),
            top_k => {k},
            distance_type => 'COSINE'
        )
        """
        results = self.bq_client.query(sql).result()
        return [f"[{row['category']} Q: {row.question} A: {row['answer']}]" for row in results]

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
            model=settings.GENERATION_MODEL,
            contents=prompt
        )

        contextualization_query = response.text.strip()
        logger.info(f"Original Query: {query}")
        logger.info(f"Contextualization Query: {contextualization_query}")

        return contextualization_query
    
    def generate_answer(self, query, history=[]):
        standalone_query = self.contextualization_query(query, history)
        docs = self.search(standalone_query, k=3)
        context = "\n\n".join(docs)

        prompt = f"""
        KONTEKS:
        {context}

        PERTANYAAN PELANGGAN: {query}
        """

        response_stream = client.models.generate_content_stream(
            model=settings.GENERATION_MODEL,
            contents=prompt,
            config=GenerateContentConfig(
                temperature=0.2,
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
        return response_stream, {"retrieved_docs": docs}
