import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    backend_root = Path(__file__).resolve().parent.parent
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

import os
import logging
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
logger = logging.getLogger(__name__)

# Services
repository_service = RepositoryService()
repository_manager = RepositoryManager()
architecture_service: ArchitectureService | None = None
file_service: FileService | None = None


def setup_active_services(repo_path: str):
    global architecture_service, file_service
    architecture_service = ArchitectureService(repo_path)
    file_service = FileService(repo_path)


# Restore the previously selected imported repository, if it still exists.
def auto_load_saved_repository():
    if repository_manager.is_loaded():
        return

    saved_repository = next(
        (
            repository
            for repository in repository_manager.get_saved_repositories()
            if repository["repository_path"]
            == repository_manager.active_repository_path
            and repository.get("repo_url")
            and os.path.isdir(repository["repository_path"])
        ),
        None,
    )
    if saved_repository:
        repository_manager.set_repository(
            repository_name=saved_repository["repository"],
            repository_path=saved_repository["repository_path"],
            repo_url=saved_repository.get("repo_url"),
            files=saved_repository.get("files", 0),
            chunks=saved_repository.get("chunks", 0),
        )
        setup_active_services(saved_repository["repository_path"])
    elif repository_manager.active_repository_path is not None:
        # Legacy startup used to auto-select a hard-coded local checkout and
        # save it without a repository URL. Keep it available in the saved
        # list, but require an explicit selection rather than restoring it.
        repository_manager.active_repository_path = None
        repository_manager._save_state()


auto_load_saved_repository()

# Request Models

class RepositoryImportRequest(BaseModel):
    repo_url: str


class RepositoryActivationRequest(BaseModel):
    repository_path: str


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
        saved_repository = repository_manager.get_repository_by_url(
            request.repo_url
        )
        if (
            saved_repository
            and os.path.isdir(saved_repository["repository_path"])
        ):
            repository_manager.set_repository(
                repository_name=saved_repository["repository"],
                repository_path=saved_repository["repository_path"],
                repo_url=saved_repository.get("repo_url"),
                files=saved_repository.get("files", 0),
                chunks=saved_repository.get("chunks", 0),
            )
            setup_active_services(saved_repository["repository_path"])
            return {
                **saved_repository,
                "status": "indexed",
            }

        # Clone + load + chunk + embed + store
        result = repository_service.import_repository(request.repo_url)

        # Initialize RAG for this repository
        repository_manager.set_repository(
            repository_name=result["repository"],
            repository_path=result["repository_path"],
            repo_url=result["repo_url"],
            files=result["files"],
            chunks=result["chunks"],
        )

        setup_active_services(result["repository_path"])

        return result

    except Exception as error:
        logger.exception("Repository import failed for %s", request.repo_url)
        raise HTTPException(
            status_code=500,
            detail=f"Repository import failed: {error}",
        )


@app.get("/api/repository/saved")
def get_saved_repositories():
    return {
        "repositories": repository_manager.get_saved_repositories(),
        "active_repository_path": repository_manager.active_repository_path,
    }


@app.post("/api/repository/activate")
def activate_repository(request: RepositoryActivationRequest):
    repository = next(
        (
            item
            for item in repository_manager.get_saved_repositories()
            if item["repository_path"] == request.repository_path
        ),
        None,
    )
    if repository is None or not os.path.isdir(repository["repository_path"]):
        raise HTTPException(
            status_code=404,
            detail="That repository is not available. Import it again.",
        )

    try:
        repository_manager.set_repository(
            repository_name=repository["repository"],
            repository_path=repository["repository_path"],
            repo_url=repository.get("repo_url"),
            files=repository.get("files", 0),
            chunks=repository.get("chunks", 0),
        )
        setup_active_services(repository["repository_path"])
        return {
            **repository,
            "loaded": True,
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# Repository Status

@app.get("/api/repository/status")
def repository_status():
    if not repository_manager.is_loaded():
        auto_load_saved_repository()

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
        auto_load_saved_repository()

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


@app.get("/api/repository/suggestions")
def get_repository_suggestions():
    if not repository_manager.is_loaded():
        auto_load_saved_repository()

    if not repository_manager.is_loaded():
        raise HTTPException(
            status_code=404,
            detail="Import a repository before requesting suggestions.",
        )

    global architecture_service
    if architecture_service is None:
        setup_active_services(repository_manager.get_repository_path())

    suggestions = []
    for flow in architecture_service.get_feature_flows():
        frontend_api = flow.get("frontend_api") or {}
        route = flow.get("route") or {}
        controller = flow.get("controller") or {}
        function_name = (
            frontend_api.get("function")
            or flow.get("name")
            or controller.get("controller_function")
        )
        endpoint = (
            route.get("path")
            or frontend_api.get("resolved_endpoint")
            or frontend_api.get("endpoint")
        )
        controller_function = controller.get("controller_function")

        if function_name and endpoint:
            question = (
                f"How does {function_name} handle {endpoint}"
                f"{f' through {controller_function}' if controller_function else ''}?"
            )
        elif function_name:
            question = (
                f"What does {function_name} do in this codebase, "
                "and what does it depend on?"
            )
        elif endpoint:
            question = f"Where is {endpoint} handled and what does it do?"
        else:
            continue

        if question not in suggestions:
            suggestions.append(question)
        if len(suggestions) == 4:
            break

    if not suggestions:
        ignored_directories = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "dist",
            "build",
            ".next",
        }
        source_extensions = {
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".go",
            ".rs",
        }
        source_files = []
        repository_path = repository_manager.get_repository_path()
        for root, directories, filenames in os.walk(repository_path):
            directories[:] = [
                directory
                for directory in directories
                if directory not in ignored_directories
            ]
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() in source_extensions:
                    source_files.append(
                        os.path.relpath(
                            os.path.join(root, filename),
                            repository_path,
                        ).replace(os.sep, "/")
                    )
            if len(source_files) >= 4:
                break

        suggestions = [
            f"What is the role of {file_path} in this codebase?"
            for file_path in source_files[:4]
        ]

    return {
        "repository": repository_manager.get_repository(),
        "suggestions": suggestions,
    }


# =========================
# Chat
# =========================

@app.post("/api/chat")
def chat(request: ChatRequest):
    if not repository_manager.is_loaded():
        auto_load_saved_repository()

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
        auto_load_saved_repository()

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
        auto_load_saved_repository()

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
        auto_load_saved_repository()

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
        auto_load_saved_repository()

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