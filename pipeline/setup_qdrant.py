import os
import sys
import psycopg2

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.embedding import get_embedding_batch
from app.logger import get_logger

logger = get_logger()
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "faq-db"),
    "user": os.getenv("POSTGRES_USER", "postgres"), 
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432))
}

def setup_qdrant():
    logger.info("Connecting to PostgreSQL to fetch data")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("SELECT id, category, question, answer, source, language FROM faqs")
        rows = cur.fetchall()

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error: {e}")
        return

    if not rows:
        logger.warning("No data found in PostgreSQL")
        return

    texts_to_embed = []
    payloads = []
    qdrant_ids = []

    for row in rows:
        db_id, category, question, answer, source, language = row
        text = f"Q: {question}\nA: {answer}"
        texts_to_embed.append(text)
        qdrant_ids.append(db_id)
        payloads.append({
            "category": category,
            "source": source,
            "language": language,
            "text": text
        })

    logger.info("Connecting to Qdrant")
    embeddings = get_embedding_batch(texts_to_embed)
    
    # KONEKSI QDRANT YANG SUDAH DINAMIS
    q_client_host = os.getenv("QDRANT_HOST", "localhost")
    q_client_port = os.getenv("QDRANT_PORT", 6333)
    q_api_key = os.getenv("QDRANT_API_KEY", None)

    if q_api_key:
        logger.info(f"Connecting to QDRANT CLOUD at {q_client_host}")
        q_client = QdrantClient(
            url=q_client_host,
            api_key=q_api_key,
            timeout=60
        )
    else:
        logger.info(f"Connecting to QDRANT LOCAL at {q_client_host}:{q_client_port}")
        q_client = QdrantClient(host=q_client_host, port=q_client_port)

    collection_name = "faq_collection"

    if q_client.collection_exists(collection_name):
        q_client.delete_collection(collection_name)

    q_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=3072,
            distance=models.Distance.COSINE
        )
    )

    points = []
    for idx in range(len(rows)):
        points.append(
            models.PointStruct(
                id=qdrant_ids[idx],
                vector=embeddings[idx],
                payload=payloads[idx]
            )
        )
        
    q_client.upsert(
        collection_name=collection_name,
        points=points,
    )

    logger.info(f"Successfully upserted {len(points)} points to Qdrant")

if __name__ == "__main__":
    setup_qdrant()
