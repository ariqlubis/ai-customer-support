from .config import client, EMBEDDING_MODEL
from google.genai.types import EmbedContentConfig
import time

def get_embedding(text: str):
    """Gets embedding for a single string."""
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[text],
        config=EmbedContentConfig(task_type='RETRIEVAL_QUERY')
    )
    return response.embeddings[0].values

def get_embedding_batch(texts: list[str], batch_size: int=50):
    """Gets embeddings for a list of strings in batches."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=EmbedContentConfig(task_type='RETRIEVAL_DOCUMENT')
        )
        # Move extend inside the loop
        all_embeddings.extend([emb.values for emb in response.embeddings])
        # Small delay between batches to avoid rate limits
        time.sleep(1) 
    return all_embeddings
