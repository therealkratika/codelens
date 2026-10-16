from fastapi import APIRouter

from app.core.state import app_state


router = APIRouter()


@router.get("/")
def root():
    manager = app_state.repository_manager
    return {
        "name": "CodeLens API",
        "status": "running",
        "repository": (
            manager.get_repository() if manager.is_loaded() else None
        ),
    }


@router.get("/health")
@router.get("/api/health")
def health():
    return {"status": "ok"}
