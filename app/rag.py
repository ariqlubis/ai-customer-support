import os
from .embedding import get_embedding
from .config import settings, client
from .logger import get_logger
from google.cloud import bigquery
from google.genai.types import GenerateContentConfig

logger = get_logger()

SYSTEM_INSTRUCTION = """
Anda adalah AI Customer Support Assistant yang ramah dan professional.
Tugas utama Anda adalah memberikan jawaban akurat berdasarkan KONTEKS yang diberikan.

ATURAN PENTING:
1. Jawab berdasarkan informasi di dalam KONTEKS. Anda BOLEH merangkum atau menggabungkan informasi dari beberapa dokumen
yang berbeda dalam KONTEKS untuk memberikan jawaban yang lengkap (misal: menggabungkan syarat dokumen dan syarat usia kendaraan).
2. Jika informasi BENAR-BENAR tidak ada di KONTEKS, tolak dengan sopan. Jangan mengarang data.
3. Terjemahkan istilah umum pengguna (seperti "jasa", "produk", "ngutang") menjadi istilah resmi BFI (seperti "pembiayaan",
atau "pinjaman") secara natural dalam jawaban Anda. 
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
        pertanyaan mandiri yang spesifik untuk pencarian dokumen FAQ.

        TUGAS ANDA:
        1. Selesaikan kata ganti (misal: "itu", menjadi "BPKB mobil").
        2. Terjemahkan kata umum/gaul menjadi istilah resmi (misal: "jasa kalian" menjadi "produk pinjaman", "syarat ngutang"
        menjadi "persyaratan pengajuan pembiayaan").
        3. JANGAN menjawab pertanyaannya, cukup kembalikan teks pertanyaannya saja

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
        docs = self.search(standalone_query, k=5)
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
