import os
from google import genai
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_ID: str = 'ai-customer-support-c'
    LOCATION: str = "us-central1"
    EMBEDDING_MODEL: str = 'text-embedding-004'
    GENERATION_MODEL: str = 'gemini-2.5-flash'
    TOP_K: int = 5

    class Config:
        env_file = ".env"

settings = Settings()

client = genai.Client(
    vertexai=True,
    project=settings.PROJECT_ID,
    location=settings.LOCATION
)