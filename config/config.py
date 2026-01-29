import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
    ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
    ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE")
    RAG_MODEL = "llama-3.1-8b-instant"
    POSTGRES_DB_PASSWORD = os.getenv("POSTGRES_DB_PASSWORD")