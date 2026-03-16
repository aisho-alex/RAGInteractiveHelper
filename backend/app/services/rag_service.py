import os
import requests
from typing import List, Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.db import get_chroma_client

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://routerai.ru/api/v1")
CHAT_MODEL = os.getenv("CHAT_MODEL", "google/gemini-3.1-flash-lite-preview")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")


def get_embeddings_vector(text: str) -> List[float]:
    """Получение эмбеддинга через routerai.ru API"""
    response = requests.post(
        f"{OPENAI_API_BASE}/embeddings",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
            "encoding_format": "float"
        }
    )
    response.raise_for_status()
    data = response.json()
    return data["data"][0]["embedding"]


class EmbeddingsWrapper:
    """Обёртка для совместимости с langchain"""
    def embed_query(self, text: str) -> List[float]:
        return get_embeddings_vector(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [get_embeddings_vector(text) for text in texts]


def get_embeddings():
    """Получение модели эмбеддингов через routerai.ru"""
    return EmbeddingsWrapper()


def get_chat_model():
    """Получение чат-модели"""
    return ChatOpenAI(
        model=CHAT_MODEL,
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_API_BASE,
        temperature=0.0,
        max_tokens=8192,
    )


def add_document(text: str, metadata: dict = None) -> str:
    """Добавление документа в векторную базу"""
    client = get_chroma_client()
    collection = client.get_or_create_collection("documents")
    embeddings = get_embeddings()
    
    # Разбиваем текст на чанки
    chunks = split_text(text)
    
    ids = []
    for i, chunk in enumerate(chunks):
        doc_id = f"doc_{len(collection.get()['ids'])}_{i}"
        embedding = embeddings.embed_query(chunk)
        
        doc_metadata = {
            **(metadata or {}),
            "chunk": i,
            "text": chunk
        }
        
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[doc_metadata],
            documents=[chunk]
        )
        ids.append(doc_id)
    
    return ids[0] if len(ids) == 1 else f"{len(ids)} chunks"


def split_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Разбиение текста на чанки с перекрытием"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def search_documents(query: str, top_k: int = 3, neighbors: int = 1) -> List[Tuple[str, dict]]:
    """Поиск релевантных документов с добавлением соседних чанков"""
    client = get_chroma_client()
    collection = client.get_or_create_collection("documents")
    embeddings = get_embeddings()
    
    query_embedding = embeddings.embed_query(query)
    
    # Запрашиваем больше результатов для захвата контекста
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * (neighbors * 2 + 1),
        include=["metadatas", "documents"]
    )
    
    documents = []
    if results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            documents.append((doc, metadata))
    
    # Сортируем чанки по порядку (по chunk index) для восстановления контекста
    documents.sort(key=lambda x: x[1].get("chunk", 0))
    
    return documents


def generate_answer(query: str, documents: List[Tuple[str, dict]]) -> str:
    """Генерация ответа строго по документам"""
    model = get_chat_model()
    
    # Берём больше чанков для полноты контекста
    context = "\n\n".join([doc for doc, _ in documents[:9]])
    
    system_prompt = """Ты ассистент, который отвечает ТОЛЬКО на основе предоставленных документов.
    
Правила:
1. Используй исключительно информацию из предоставленных документов
2. Если в документах нет информации для ответа, скажи: "В предоставленных документах нет информации для ответа на этот вопрос"
3. Не добавляй информацию из своих знаний
4. Будь точен и конкретен
5. Цитируй документы, когда это возможно"""

    user_prompt = f"""Контекст из документов:
{context}

Вопрос пользователя: {query}

Ответ:"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = model.invoke(messages)
    return response.content
