import json
import os
import sys
import pickle
import numpy as np
import faiss

project_root = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(project_root)

from app.embedding import get_embedding_batch
from app.logger import get_logger

logger = get_logger()

DATA_DIR = os.path.join(project_root, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "faq.json")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.pkl")

def run_pipeline():
    logger.info("Starting data ingestion ETL")
    logger.info("1. Extract: Loading raw data")
    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    logger.info("2. Transform: Formatting text and generating embeddings")
    texts = []
    metadata = []

    for i in data:
        text = f"Q: {i['question']}\nA: {i['answer']}"
        texts.append(text)
        metadata.append(i)

    embeddings = get_embedding_batch(texts)
    embeddings_np = np.array(embeddings).astype('float32')

    logger.info("3. Load: Building and saving vector DB to disk")
    dims = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dims)
    index.add(embeddings_np)
    faiss.write_index(index, FAISS_INDEX_PATH)

    with open(METADATA_PATH, 'wb') as f:
        pickle.dump({
            "texts": texts,
            "metadata": metadata
        }, f)

    logger.info("ETL pipeline completed successfully")

if __name__ == "__main__":
    run_pipeline()
 

