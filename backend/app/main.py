from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import rag, documents
from app.db import init_db

app = FastAPI(
    title="RAG API",
    description="API для RAG системы с ответами строго по документам",
    version="1.0.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация БД при старте
init_db()

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(rag.router, prefix="/api", tags=["rag"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
