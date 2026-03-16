import chromadb
from chromadb.config import Settings
import os
from dotenv import load_dotenv

load_dotenv()

_chroma_client = None


def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/embeddings")
        os.makedirs(persist_dir, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
    return _chroma_client


def init_db():
    """Инициализация базы данных векторов"""
    client = get_chroma_client()
    # Создаём коллекцию по умолчанию
    client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )
