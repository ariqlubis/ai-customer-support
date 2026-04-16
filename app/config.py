import os
from google import genai

PROJECT_ID = 'idx-doc-intelligence'
LOCATION = "asia-southeast1"

EMBEDDING_MODEL = 'gemini-embedding-001'
GENERATION_MODEL = 'gemini-2.5-flash'

TOP_K = 5

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)