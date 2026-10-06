from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.repository_service import RepositoryService
from app.repository_manager import RepositoryManager


app = FastAPI(
    title="CodeLens API",
    description="AI Codebase Intelligence Backend",
    version="1.0.0"
)
# Services
repository_service = RepositoryService()
repository_manager = RepositoryManager()

# Request Models

class RepositoryImportRequest(BaseModel):
    repo_url: str


class ChatRequest(BaseModel):
    question: str

# Root

@app.get("/")
def root():

    return {
        "name": "CodeLens API",
        "status": "running"
    }

# Repository Import

@app.post("/api/repository/import")
def import_repository(
    request: RepositoryImportRequest
):

    try:

        # Clone + load + chunk + embed + store
        result = repository_service.import_repository(
            request.repo_url
        )

        # Initialize RAG for this repository
        repository_manager.set_repository(
            repository_name=result["repository"],
            repository_path=result["repository_path"]
        )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

# Repository Status

@app.get("/api/repository/status")
def repository_status():

    if not repository_manager.is_loaded():

        return {
            "loaded": False,
            "repository": None
        }

    return {
        "loaded": True,
        "repository": repository_manager.get_repository(),
        "repository_path": repository_manager.get_repository_path()
    }


@app.get("/api/repository")
def get_repository():

    if not repository_manager.is_loaded():
        raise HTTPException(
            status_code=404,
            detail="No repository has been imported yet."
        )

    return {
        "repository": repository_manager.get_repository(),
        "repository_path": repository_manager.get_repository_path(),
        "loaded": True
    }


# =========================
# Chat
# =========================

@app.post("/api/chat")
def chat(request: ChatRequest):

    if not repository_manager.is_loaded():

        raise HTTPException(
            status_code=400,
            detail="No repository has been imported yet."
        )

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        rag_pipeline = (
            repository_manager
            .get_rag_pipeline()
        )

        result = rag_pipeline.answer(
            request.question
        )

        return {
            "repository": repository_manager.get_repository(),
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )