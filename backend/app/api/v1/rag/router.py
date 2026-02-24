from fastapi import APIRouter, Depends, File, UploadFile

from app.core.errors import AppError
from app.rag.service import RAGService

router = APIRouter()


def get_rag_service() -> RAGService:
    return RAGService()


@router.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...), service: RAGService = Depends(get_rag_service)) -> dict:
    if not file.filename:
        raise AppError("missing_filename", status_code=400)
    if not file.filename.lower().endswith(".pdf"):
        raise AppError("invalid_file_type", status_code=400)

    data = await file.read()
    count = await service.ingest_pdf_bytes(data, file.filename)
    return {"chunks": count, "source": file.filename}


@router.post("/upload-text")
async def upload_text_file(file: UploadFile = File(...)) -> dict:
    """Upload a text-based file and return its content for chat context"""
    if not file.filename:
        raise AppError("missing_filename", status_code=400)
    
    # Allow common text-based file types
    allowed_extensions = {'.txt', '.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cpp', '.c', 
                         '.html', '.css', '.json', '.md', '.xml', '.yaml', '.yml', '.sh'}
    
    file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if file_ext not in allowed_extensions:
        raise AppError("invalid_file_type", status_code=400, 
                      detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}")
    
    try:
        content = await file.read()
        text_content = content.decode('utf-8')
        return {
            "filename": file.filename,
            "content": text_content,
            "size": len(content),
            "type": file_ext
        }
    except UnicodeDecodeError:
        raise AppError("file_decode_error", status_code=400, 
                      detail="File must be text-based and UTF-8 encoded")
