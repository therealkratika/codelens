import logging

from fastapi import APIRouter, HTTPException

from app.core.state import app_state
from app.schemas.chat import ChatRequest
from app.schemas.chat import ChatSessionCreateRequest, ChatSessionRenameRequest
from app.services.chat_service import ChatService
from app.services.repository_import_service import RepositoryImportService


logger = logging.getLogger(__name__)
router = APIRouter()
import_service = RepositoryImportService(app_state)
chat_service = ChatService(app_state)


@router.get("/api/chat/sessions")
def list_chat_sessions():
    import_service.require_active_repository()
    return {"sessions": chat_service.list_sessions()}


@router.post("/api/chat/sessions")
def create_chat_session(request: ChatSessionCreateRequest | None = None):
    import_service.require_active_repository()
    session = chat_service.create_session(request.title if request else None)
    return {"session": session}


@router.get("/api/chat/sessions/{session_id}")
def get_chat_session(session_id: str):
    import_service.require_active_repository()
    return {"session": chat_service.get_session(session_id)}


@router.delete("/api/chat/sessions/{session_id}")
def delete_chat_session(session_id: str):
    import_service.require_active_repository()
    return chat_service.delete_session(session_id)


@router.patch("/api/chat/sessions/{session_id}")
def rename_chat_session(
    session_id: str,
    request: ChatSessionRenameRequest,
):
    import_service.require_active_repository()
    return {"session": chat_service.rename_session(session_id, request.title)}


@router.post("/api/chat")
@router.post("/chat")
def chat(request: ChatRequest):
    import_service.require_active_repository()
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        return chat_service.answer(request.question, request.session_id)
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="Chat failed. Check the backend logs for details.",
        ) from error
