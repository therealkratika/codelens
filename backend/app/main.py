
import logging
import os
import sys
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure backend directory is importable.
BACKEND_ROOT = Path(__file__).resolve().parent.parent

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.repository_manager import RepositoryManager

# APPLICATION
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CodeLens API",
    description="AI Codebase Intelligence Backend",
    version="1.0.0",
)

default_cors_origins = [
    "https://codelens-flax.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

configured_cors_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CODELENS_CORS_ORIGINS", ""
    ).split(",")
    if origin.strip()
]

cors_origins = list(
    dict.fromkeys(
        default_cors_origins + configured_cors_origins
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# SERVICE STATE

repository_service = None
architecture_service = None
file_service = None

repository_import_lock = Lock()
repository_import_jobs = {}

repository_manager = RepositoryManager()


# REQUEST MODELS

class RepositoryImportRequest(BaseModel):
    repo_url: str = Field(min_length=1)


class RepositoryActivationRequest(BaseModel):
    repository_path: str = Field(min_length=1)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)

# LAZY SERVICE HELPERS

def get_repository_service():
    """Create the repository service only when needed."""
    global repository_service

    if repository_service is None:
        from app.repository_service import RepositoryService
        repository_service = RepositoryService()

    return repository_service


def get_architecture_service(repo_path: str):
    """Return an architecture service for the requested repo."""
    global architecture_service

    if (
        architecture_service is None
        or getattr(
            architecture_service,
            "repository_path",
            None,
        ) != repo_path
    ):
        from app.architecture_service import ArchitectureService

        architecture_service = ArchitectureService(repo_path)

    return architecture_service


def get_file_service(repo_path: str):
    """Return a file service for the requested repo."""
    global file_service

    if (
        file_service is None
        or getattr(
            file_service,
            "repository_path",
            None,
        ) != repo_path
    ):
        from app.file_service import FileService

        file_service = FileService(repo_path)

    return file_service


def setup_active_services(repo_path: str):
    """
    Invalidate repository-dependent service caches when
    the active repository changes.
    """
    global architecture_service, file_service

    architecture_service = None
    file_service = None

    logger.info("Active repository changed to: %s", repo_path)

# REPOSITORY RESTORATION

def auto_load_saved_repository():
    """
    Restore the selected saved repository if its directory
    still exists. This function is called only when needed.
    """
    if repository_manager.is_loaded():
        return True

    active_path = repository_manager.active_repository_path

    if not active_path:
        return False

    saved_repository = next(
        (
            repository
            for repository in repository_manager.get_saved_repositories()
            if repository.get("repository_path") == active_path
            and repository.get("repo_url")
            and os.path.isdir(
                repository.get("repository_path", "")
            )
        ),
        None,
    )

    if saved_repository is None:
        repository_manager.active_repository_path = None
        repository_manager._save_state()
        return False

    try:
        repository_manager.set_repository(
            repository_name=saved_repository["repository"],
            repository_path=saved_repository["repository_path"],
            repo_url=saved_repository.get("repo_url"),
            files=saved_repository.get("files", 0),
            chunks=saved_repository.get("chunks", 0),
        )

        setup_active_services(
            saved_repository["repository_path"]
        )

        return True

    except Exception:
        logger.exception("Failed to restore saved repository")
        return False


def require_active_repository():
    """Return the active repository path or raise an HTTP error."""
    if not repository_manager.is_loaded():
        auto_load_saved_repository()

    if not repository_manager.is_loaded():
        raise HTTPException(
            status_code=404,
            detail="No repository is currently active. Import or activate a repository first.",
        )

    return repository_manager.get_repository_path()


# REPOSITORY IMPORT

def perform_repository_import(repo_url: str):
    """
    Import or reuse a repository, then make it active.

    Repository cloning and indexing are handled by RepositoryService.
    """
    saved_repository = repository_manager.get_repository_by_url(
        repo_url
    )

    if (
        saved_repository
        and os.path.isdir(
            saved_repository.get("repository_path", "")
        )
    ):
        repository_manager.set_repository(
            repository_name=saved_repository["repository"],
            repository_path=saved_repository["repository_path"],
            repo_url=saved_repository.get("repo_url"),
            files=saved_repository.get("files", 0),
            chunks=saved_repository.get("chunks", 0),
        )

        setup_active_services(
            saved_repository["repository_path"]
        )

        return {
            **saved_repository,
            "status": "indexed",
        }

    service = get_repository_service()
    result = service.import_repository(repo_url)

    repository_manager.set_repository(
        repository_name=result["repository"],
        repository_path=result["repository_path"],
        repo_url=result["repo_url"],
        files=result["files"],
        chunks=result["chunks"],
    )

    setup_active_services(result["repository_path"])

    return result


def run_repository_import(job_id: str, repo_url: str):
    """Execute an import job and always release its import lock."""
    try:
        job = repository_import_jobs.get(job_id)

        if job is None:
            logger.error("Import job %s was not found", job_id)
            return

        job["status"] = "running"

        result = perform_repository_import(repo_url)

        job["result"] = result
        job["error"] = None
        job["status"] = "completed"

        logger.info(
            "Repository import completed for %s",
            repo_url,
        )

    except Exception as error:
        logger.exception(
            "Repository import failed for %s",
            repo_url,
        )

        job = repository_import_jobs.get(job_id)

        if job is not None:
            job["error"] = (
                f"Repository import failed: {error}"
            )
            job["status"] = "failed"

    finally:
        repository_import_lock.release()


@app.post("/api/repository/import", status_code=202)
def import_repository(
    request: RepositoryImportRequest,
    background_tasks: BackgroundTasks,
):
    repo_url = request.repo_url.strip()

    if not repo_url:
        raise HTTPException(
            status_code=400,
            detail="Repository URL cannot be empty.",
        )

    if not repository_import_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409,
            detail="Another repository import is already in progress. Please wait for it to finish.",
        )

    job_id = str(uuid4())

    repository_import_jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "result": None,
        "error": None,
    }

    try:
        background_tasks.add_task(
            run_repository_import,
            job_id,
            repo_url,
        )
    except Exception:
        repository_import_jobs.pop(job_id, None)
        repository_import_lock.release()
        logger.exception("Could not schedule import job %s", job_id)

        raise HTTPException(
            status_code=500,
            detail="Could not schedule repository import.",
        )

    return dict(repository_import_jobs[job_id])


@app.get("/api/repository/import/{job_id}")
def get_repository_import_status(job_id: str):
    job = repository_import_jobs.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Repository import job was not found.",
        )

    return dict(job)


# ROOT AND HEALTH

@app.get("/")
def root():
    return {
        "name": "CodeLens API",
        "status": "running",
        "repository": (
            repository_manager.get_repository()
            if repository_manager.is_loaded()
            else None
        ),
    }


@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok"}


# SAVED REPOSITORIES

@app.get("/api/repository/saved")
def get_saved_repositories():
    return {
        "repositories": repository_manager.get_saved_repositories(),
        "active_repository_path": (
            repository_manager.active_repository_path
        ),
    }


# ACTIVATE REPOSITORY

@app.post("/api/repository/activate")
@app.post("/repository/activate")
def activate_repository(
    request: RepositoryActivationRequest,
):
    req_path = request.repository_path
    req_folder = Path(req_path).name

    repository = next(
        (
            item
            for item in repository_manager.get_saved_repositories()
            if item.get("repository_path") == req_path
            or item.get("normalized_url") == req_path
            or Path(item.get("repository_path", "")).name == req_folder
        ),
        None,
    )

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="That repository is unavailable. Import it again.",
        )

    current_path = repository.get("repository_path", "")
    folder_name = Path(current_path).name
    local_target = BACKEND_ROOT / "repositories" / folder_name

    if os.path.isdir(current_path):
        target_path = current_path
    elif local_target.is_dir():
        target_path = str(local_target)
        repository["repository_path"] = target_path
        from app.repository_storage import save_repository
        save_repository(repository)
    elif repository.get("repo_url"):
        try:
            from app.github.clone_repo import clone_repository
            from app.repository_storage import save_repository
            target_path = clone_repository(
                repository["repo_url"],
                repository.get("repository", folder_name),
            )
            repository["repository_path"] = target_path
            save_repository(repository)
        except Exception:
            logger.exception("Failed to auto-clone repository on activation")
            raise HTTPException(
                status_code=500,
                detail="Could not restore repository files on server. Import it again.",
            )
    else:
        raise HTTPException(
            status_code=404,
            detail="That repository is unavailable. Import it again.",
        )

    try:
        repository_manager.set_repository(
            repository_name=repository["repository"],
            repository_path=target_path,
            repo_url=repository.get("repo_url"),
            files=repository.get("files", 0),
            chunks=repository.get("chunks", 0),
        )

        setup_active_services(target_path)

        return {
            **repository,
            "repository_path": target_path,
            "loaded": True,
        }

    except Exception:
        logger.exception("Repository activation failed")

        raise HTTPException(
            status_code=500,
            detail="Repository activation failed. Check the backend logs.",
        )


# REPOSITORY STATUS

@app.get("/api/repository/status")
def repository_status():
    if not repository_manager.is_loaded():
        auto_load_saved_repository()

    if not repository_manager.is_loaded():
        return {
            "loaded": False,
            "repository": None,
        }

    return {
        "loaded": True,
        "repository": repository_manager.get_repository(),
        "repository_path": repository_manager.get_repository_path(),
    }


@app.get("/api/repository")
def get_repository():
    repo_path = require_active_repository()

    return {
        "repository": repository_manager.get_repository(),
        "repository_path": repo_path,
        "loaded": True,
    }


# REPOSITORY SUGGESTIONS

@app.get("/api/repository/suggestions")
def get_repository_suggestions():
    repo_path = require_active_repository()
    architecture = get_architecture_service(repo_path)

    try:
        suggestions = []

        for flow in architecture.get_feature_flows():
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

            controller_function = controller.get(
                "controller_function"
            )

            if function_name and endpoint:
                question = (
                    f"How does {function_name} handle {endpoint}"
                    f"{f' through {controller_function}' if controller_function else ''}?"
                )
            elif function_name:
                question = (
                    f"What does {function_name} do in this "
                    "codebase, and what does it depend on?"
                )
            elif endpoint:
                question = (
                    f"Where is {endpoint} handled and what does it do?"
                )
            else:
                continue

            if question not in suggestions:
                suggestions.append(question)

            if len(suggestions) >= 4:
                break

        if not suggestions:
            ignored_directories = {
                ".git", "node_modules", "venv", ".venv",
                "__pycache__", "dist", "build", ".next",
                "coverage", ".cache", "out", "target",
            }

            source_extensions = {
                ".py", ".js", ".jsx", ".ts", ".tsx",
                ".java", ".go", ".rs",
            }

            source_files = []

            for root, directories, filenames in os.walk(repo_path):
                directories[:] = [
                    directory
                    for directory in directories
                    if directory not in ignored_directories
                ]

                for filename in filenames:
                    if Path(filename).suffix.lower() in source_extensions:
                        source_files.append(
                            os.path.relpath(
                                os.path.join(root, filename),
                                repo_path,
                            ).replace(os.sep, "/")
                        )

                        if len(source_files) >= 4:
                            break

                if len(source_files) >= 4:
                    break

            suggestions = [
                f"What is the role of {file_path} in this codebase?"
                for file_path in source_files
            ]

        return {
            "repository": repository_manager.get_repository(),
            "suggestions": suggestions,
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("Repository suggestions failed")

        raise HTTPException(
            status_code=500,
            detail="Could not generate repository suggestions.",
        )


# ============================================================
# CHAT
# ============================================================

@app.post("/api/chat")
@app.post("/chat")
def chat(request: ChatRequest):
    require_active_repository()

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        rag_pipeline = repository_manager.get_rag_pipeline()
        result = rag_pipeline.answer(request.question)

        return {
            "repository": repository_manager.get_repository(),
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except Exception:
        logger.exception("Chat request failed")

        raise HTTPException(
            status_code=500,
            detail="Chat failed. Check the backend logs for details.",
        )


# ARCHITECTURE FLOWS

@app.get("/api/architecture/flows")
def get_architecture_flows():
    repo_path = require_active_repository()
    architecture = get_architecture_service(repo_path)

    try:
        flows = architecture.get_feature_flows()

        return {
            "repository": repository_manager.get_repository(),
            "flows": flows,
            "total": len(flows),
        }

    except Exception:
        logger.exception("Architecture flow request failed")

        raise HTTPException(
            status_code=500,
            detail="Could not load architecture flows.",
        )


# ============================================================
# ARCHITECTURE GRAPH
# ============================================================

@app.get("/api/architecture/graph")
def get_architecture_graph():
    repo_path = require_active_repository()
    architecture = get_architecture_service(repo_path)

    try:
        graph = architecture.get_code_graph()

        return {
            "repository": repository_manager.get_repository(),
            **graph,
        }

    except Exception:
        logger.exception("Architecture graph request failed")

        raise HTTPException(
            status_code=500,
            detail="Could not load the architecture graph.",
        )


# FILE TREE

@app.get("/api/files/tree")
def get_file_tree():
    repo_path = require_active_repository()
    service = get_file_service(repo_path)

    try:
        tree = service.get_file_tree()

        return {
            "repository": repository_manager.get_repository(),
            "tree": tree,
        }

    except Exception:
        logger.exception("File tree request failed")

        raise HTTPException(
            status_code=500,
            detail="Could not load the file tree.",
        )


# FILE CONTENT

@app.get("/api/files/content")
def get_file_content(
    path: str = Query(
        ...,
        min_length=1,
        description="Relative path to a file in the active repository",
    ),
):
    repo_path = require_active_repository()
    service = get_file_service(repo_path)

    try:
        content_data = service.get_file_content(path)

        return {
            "repository": repository_manager.get_repository(),
            **content_data,
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="File was not found in the active repository.",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        logger.exception("File content request failed")

        raise HTTPException(
            status_code=500,
            detail="Could not read the requested file.",
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
