from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import search_documents, generate_answer

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_handler(request: QueryRequest):
    """Обработка запроса пользователя с использованием RAG"""
    try:
        # Поиск релевантных документов с соседними чанками
        documents = search_documents(request.query, top_k=5, neighbors=1)
        
        if not documents:
            return QueryResponse(
                answer="В базе знаний нет документов для обработки запроса. Пожалуйста, загрузите документы сначала.",
                sources=[]
            )
        
        # Генерация ответа
        answer = generate_answer(request.query, documents)
        
        # Формирование источников
        sources = []
        for doc, metadata in documents[:9]:
            sources.append({
                "content": doc[:200] + "..." if len(doc) > 200 else doc,
                "metadata": metadata
            })
        
        return QueryResponse(answer=answer, sources=sources)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
