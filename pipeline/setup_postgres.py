from httpcore import __name
import psycopg2
import json
import os, sys
import psycopg2
from psycopg2.extras import execute_values

project_root = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(project_root)

from app.logger import get_logger

logger = get_logger()

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "faq-db"),
    "user": os.getenv("POSTGRES_USER", "postgres"), 
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432))
}


def setup_database():
    conn = None
    cur = None

    logger.info("Connecting to PostgreSQL")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        logger.info("Creating table 'faqs'")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS faqs (
                id SERIAL PRIMARY KEY,
                category VARCHAR(100),
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                source VARCHAR(100),
                language VARCHAR(10)
            )
        """)

        cur.execute("TRUNCATE TABLE faqs RESTART IDENTITY")
        json_path = os.path.join(project_root, "data", "faq.json")
        logger.info(f"Reading data from {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        insert_query = """
            INSERT INTO faqs (category, question, answer, source, language)
            VALUES %s
        """

        values = [
            (item.get("category", ""), item.get("question", ""), item.get("answer", ""), item.get("source", ""), item.get("language", ""))
            for item in data
        ]
        logger.info(f"Inserting {len(values)} rows to database")
        execute_values(cur, insert_query, values)

        conn.commit()
        logger.info("Completed, database is ready")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            logger.info("PostgreSQL connection closed")

if __name__ == "__main__":
    setup_database()