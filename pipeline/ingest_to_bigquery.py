import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.logger import get_logger
from google.cloud import bigquery
from app.embedding import get_embedding_batch
from app.config import settings

logger = get_logger()

def run_ingestion():
    client = bigquery.Client(project=settings.PROJECT_ID)
    table_id = f"{settings.PROJECT_ID}.faq_data.faqs"

    with open('data/faq.json', 'r') as f:
        faqs = json.load(f)

    texts = [f"Q: {faq['question']} A: {faq['answer']}" for faq in faqs]
    embeddings = get_embedding_batch(texts)

    rows_to_insert = []
    for i, item in enumerate(faqs):
        item['embedding'] = embeddings[i]
        rows_to_insert.append(item)

    logger.info(f"Uploading to BQ: {table_id}")
    client.query(f"DELETE FROM `{table_id}` WHERE TRUE").result()  # Clear existing data

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        logger.error(f"Errors occurred while inserting rows: {errors}")
    else:
        logger.info("Data successfully ingested into BigQuery.")

if __name__ == "__main__":
    run_ingestion()