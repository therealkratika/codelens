import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.repository_service import RepositoryService
from app.repository_manager import RepositoryManager
from app.architecture_service import ArchitectureService
from app.file_service import FileService


app = FastAPI(
    title="CodeLens API",
    description="AI Codebase Intelligence Backend",
    version="1.0.0"
)

# Services
repository_service = RepositoryService()
repository_manager = RepositoryManager()
architecture_service: ArchitectureService | None = None
file_service: FileService | None = None


def setup_active_services(repo_path: str):
    global architecture_service, file_service
    architecture_service = ArchitectureService(repo_path)
    file_service = FileService(repo_path)


# Auto-load existing repository if present
def auto_load_default_repository():
    default_repo_dir = "./repositories/Nextja_coding_battle"
    if os.path.exists(default_repo_dir) and not repository_manager.is_loaded():
        print(f"Auto-loading local repository from {default_repo_dir}...")
        repository_manager.set_repository(
            repository_name="Nextja_coding_battle",
            repository_path=default_repo_dir
        )
        setup_active_services(default_repo_dir)


auto_load_default_repository()

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
        "status": "running",
        "repository": repository_manager.get_repository() if repository_manager.is_loaded() else None
    }


# Repository Import

@app.post("/api/repository/import")
def import_repository(request: RepositoryImportRequest):
    try:
        # Clone + load + chunk + embed + store
        result = repository_service.import_repository(request.repo_url)

        # Initialize RAG for this repository
        repository_manager.set_repository(
            repository_name=result["repository"],
            repository_path=result["repository_path"]
        )

        setup_active_services(result["repository_path"])

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
        auto_load_default_repository()

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
        auto_load_default_repository()

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
        auto_load_default_repository()

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
        rag_pipeline = repository_manager.get_rag_pipeline()
        result = rag_pipeline.answer(request.question)

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


# =========================
# Architecture
# =========================

@app.get("/api/architecture/flows")
def get_architecture_flows():
    if not repository_manager.is_loaded():
        auto_load_default_repository()

    if not repository_manager.is_loaded():
        raise HTTPException(
            status_code=404,
            detail="No repository has been imported yet."
        )

    global architecture_service
    if architecture_service is None:
        setup_active_services(repository_manager.get_repository_path())

    try:
        flows = architecture_service.get_feature_flows()
        return {
            "repository": repository_manager.get_repository(),
            "flows": flows,
            "total": len(flows)
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/api/architecture/graph")
def get_architecture_graph():
    if not repository_manager.is_loaded():
        auto_load_default_repository()

    if not repository_manager.is_loaded():
        raise HTTPException(
            status_code=404,
            detail="No repository has been imported yet."
        )

    global architecture_service
    if architecture_service is None:
        setup_active_services(repository_manager.get_repository_path())

    try:
        graph = architecture_service.get_code_graph()
        return {
            "repository": repository_manager.get_repository(),
            **graph
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# =========================
# Files
# =========================

@app.get("/api/files/tree")
def get_file_tree():
    if not repository_manager.is_loaded():
        auto_load_default_repository()

    if not repository_manager.is_loaded():
        raise HTTPException(
            status_code=404,
            detail="No repository has been imported yet."
        )

    global file_service
    if file_service is None:
        setup_active_services(repository_manager.get_repository_path())

    try:
        tree = file_service.get_file_tree()
        return {
            "repository": repository_manager.get_repository(),
            "tree": tree
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/api/files/content")
def get_file_content(path: str = Query(..., description="Relative path to file in repository")):
    if not repository_manager.is_loaded():
        auto_load_default_repository()

    if not repository_manager.is_loaded():
        raise HTTPException(
            status_code=404,
            detail="No repository has been imported yet."
        )

    global file_service
    if file_service is None:
        setup_active_services(repository_manager.get_repository_path())

    try:
        content_data = file_service.get_file_content(path)
        return {
            "repository": repository_manager.get_repository(),
            **content_data
        }
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))