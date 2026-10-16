import logging

from fastapi import APIRouter, HTTPException

from app.core.state import app_state
from app.schemas.chat import ChatRequest
from app.services.repository_import_service import RepositoryImportService


logger = logging.getLogger(__name__)
router = APIRouter()
import_service = RepositoryImportService(app_state)


@router.post("/api/chat")
@router.post("/chat")
def chat(request: ChatRequest):
    import_service.require_active_repository()
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        manager = app_state.repository_manager
        result = manager.get_rag_pipeline().answer(request.question)
        return {
            "repository": manager.get_repository(),
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"],
        }
    except Exception as error:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="Chat failed. Check the backend logs for details.",
        ) from error
