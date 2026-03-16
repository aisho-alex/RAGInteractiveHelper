from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import pdfplumber
import io
from app.models.schemas import DocumentUpload, DocumentResponse
from app.services.rag_service import add_document, get_all_documents, get_full_document_text

router = APIRouter()


@router.get("/list")
async def list_documents():
    """Получить список всех документов и чанков"""
    return get_all_documents()


@router.get("/full")
async def get_full_document():
    """Получить полный текст документа с маппингом чанков"""
    full_text = get_full_document_text()
    
    # Получаем информацию о чанках для маппинга позиций
    all_chunks = get_all_documents()
    
    chunk_positions = []
    current_pos = 0
    
    for chunk in all_chunks:
        # Находим позицию чанка в полном тексте
        chunk_start = full_text.find(chunk["text"][:50], current_pos)
        if chunk_start >= 0:
            # Находим конец чанка (без перекрытия)
            chunk_end = chunk_start + len(chunk["text"])
            chunk_positions.append({
                "chunk": chunk["chunk"],
                "start": chunk_start,
                "end": chunk_end,
                "metadata": chunk["metadata"]
            })
            current_pos = chunk_start
    
    return {
        "text": full_text,
        "chunks": chunk_positions
    }


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    metadata: Optional[str] = Form(None)
):
    """Загрузка документа в систему"""
    try:
        import json
        doc_metadata = json.loads(metadata) if metadata else {}
        
        if file:
            # Обработка файла
            contents = await file.read()
            
            if file.filename.endswith('.pdf'):
                # Извлечение текста из PDF
                text = extract_text_from_pdf(contents)
                doc_metadata["filename"] = file.filename
                doc_metadata["type"] = "pdf"
            elif file.filename.endswith('.txt'):
                text = contents.decode('utf-8')
                doc_metadata["filename"] = file.filename
                doc_metadata["type"] = "txt"
            else:
                raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла. Используйте PDF или TXT")
        
        elif text:
            doc_metadata["type"] = "text"
        else:
            raise HTTPException(status_code=400, detail="Необходимо предоставить текст или файл")
        
        # Добавление документа в базу
        doc_id = add_document(text, doc_metadata)
        
        return DocumentResponse(
            id=doc_id,
            status="success",
            message="Документ успешно загружен и обработан"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки документа: {str(e)}")


def extract_text_from_pdf(contents: bytes) -> str:
    """Извлечение текста из PDF"""
    text = ""
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


@router.post("/upload-text", response_model=DocumentResponse)
async def upload_text(request: DocumentUpload):
    """Загрузка текста напрямую"""
    try:
        doc_id = add_document(request.text, request.metadata)
        return DocumentResponse(
            id=doc_id,
            status="success",
            message="Текст успешно загружен и обработан"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
