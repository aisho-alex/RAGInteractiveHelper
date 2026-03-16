from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    query: str = Field(..., description="Запрос пользователя")
    top_k: int = Field(default=3, description="Количество релевантных фрагментов")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Ответ на запрос")
    sources: List[dict] = Field(default_factory=list, description="Источники информации")


class DocumentUpload(BaseModel):
    text: str = Field(..., description="Текст документа")
    metadata: Optional[dict] = Field(default=None, description="Метаданные документа")


class DocumentResponse(BaseModel):
    id: str
    status: str
    message: str
