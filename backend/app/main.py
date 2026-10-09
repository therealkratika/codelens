import sys
import os
import logging
from threading import Lock
from uuid import uuid4
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
# PATH SETUP
if __package__ is None or __package__ == "":
    backend_root = Path(__file__).resolve().parent.parent

    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


# FASTAPI

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from pydantic import BaseModel

# LIGHTWEIGHT SERVICES ONLY

from app.repository_manager import RepositoryManager

# APP

app = FastAPI(
    title="CodeLens API",
    description="AI Codebase Intelligence Backend",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://codelens-qspj.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# SERVICE STATE

repository_service = None
architecture_service = None
file_service = None
repository_import_lock = Lock()
repository_import_jobs = {}

repository_manager = RepositoryManager()

# LAZY SERVICE HELPERS

def get_repository_service():
    """
    Create RepositoryService only when repository import
    is actually requested.
    """

    global repository_service

    if repository_service is None:

        from app.repository_service import RepositoryService

        repository_service = RepositoryService()

    return repository_service


def get_architecture_service(repo_path: str):
    """
    Create ArchitectureService only when architecture
    functionality is requested.
    """

    global architecture_service

    if (
        architecture_service is None
        or getattr(
            architecture_service,
            "repository_path",
            None
        ) != repo_path
    ):

        from app.architecture_service import ArchitectureService

        architecture_service = ArchitectureService(
            repo_path
        )

    return architecture_service


def get_file_service(repo_path: str):
    """
    Create FileService only when file functionality
    is requested.
    """

    global file_service

    if (
        file_service is None
        or getattr(
            file_service,
            "repository_path",
            None
        ) != repo_path
    ):

        from app.file_service import FileService

        file_service = FileService(
            repo_path
        )

    return file_service


def setup_active_services(repo_path: str):
    """
    Reset lightweight repository-dependent services.

    Heavy services remain lazy and are created only when
    their endpoint is accessed.
    """

    global architecture_service
    global file_service

    architecture_service = None
    file_service = None


# ============================================================
# AUTO LOAD SAVED REPOSITORY
# ============================================================

def auto_load_saved_repository():
    """
    Restore the previously selected repository ONLY when
    an endpoint explicitly needs it.

    IMPORTANT:
    This function is NOT called during application startup.
    """

    if repository_manager.is_loaded():
        return True

    active_path = (
        repository_manager.active_repository_path
    )

    if not active_path:
        return False

    saved_repository = next(
        (
            repository
            for repository
            in repository_manager.get_saved_repositories()

            if repository.get(
                "repository_path"
            ) == active_path

            and repository.get(
                "repo_url"
            )

            and os.path.isdir(
                repository["repository_path"]
            )
        ),
        None,
    )

    if not saved_repository:

        # Preserve the saved repository list but don't
        # automatically activate an unavailable repository.

        if (
            repository_manager.active_repository_path
            is not None
        ):

            repository_manager.active_repository_path = None
            repository_manager._save_state()

        return False

    try:

        repository_manager.set_repository(
            repository_name=saved_repository[
                "repository"
            ],

            repository_path=saved_repository[
                "repository_path"
            ],

            repo_url=saved_repository.get(
                "repo_url"
            ),

            files=saved_repository.get(
                "files",
                0
            ),

            chunks=saved_repository.get(
                "chunks",
                0
            ),
        )

        setup_active_services(
            saved_repository[
                "repository_path"
            ]
        )

        return True

    except Exception:

        logger.exception(
            "Failed to restore saved repository"
        )

        return False


# ============================================================
# REQUEST MODELS
# ============================================================

class RepositoryImportRequest(BaseModel):

    repo_url: str


class RepositoryActivationRequest(BaseModel):

    repository_path: str


class ChatRequest(BaseModel):

    question: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "CodeLens API",
        "status": "running",
        "repository": (
            repository_manager.get_repository()
            if repository_manager.is_loaded()
            else None
        )
    }


# ============================================================
# REPOSITORY IMPORT
# ============================================================

def perform_repository_import(repo_url: str):

    saved_repository = (
        repository_manager
        .get_repository_by_url(repo_url)
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
        return {**saved_repository, "status": "indexed"}

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

    repository_import_jobs[job_id]["status"] = "running"

    try:
        repository_import_jobs[job_id]["result"] = (
            perform_repository_import(repo_url)
        )
        repository_import_jobs[job_id]["status"] = "completed"
    except Exception as error:
        logger.exception(
            "Repository import failed for %s",
            repo_url
        )
        repository_import_jobs[job_id]["error"] = (
            f"Repository import failed: {error}"
        )
        repository_import_jobs[job_id]["status"] = "failed"
    finally:
        repository_import_lock.release()


@app.post("/api/repository/import", status_code=202)
def import_repository(
    request: RepositoryImportRequest,
    background_tasks: BackgroundTasks,
):
    if not repository_import_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409,
            detail="Another repository import is already in progress.",
        )

    job_id = str(uuid4())
    repository_import_jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "result": None,
        "error": None,
    }

    background_tasks.add_task(
        run_repository_import,
        job_id,
        request.repo_url,
    )
    return {**repository_import_jobs[job_id]}


@app.get("/api/repository/import/{job_id}")
def get_repository_import_status(job_id: str):
    job = repository_import_jobs.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Repository import job was not found.",
        )
    return job


# ============================================================
# SAVED REPOSITORIES
# ============================================================

@app.get("/api/repository/saved")
def get_saved_repositories():

    return {
        "repositories":
            repository_manager
            .get_saved_repositories(),

        "active_repository_path":
            repository_manager
            .active_repository_path,
    }


# ============================================================
# ACTIVATE REPOSITORY
# ============================================================

@app.post("/api/repository/activate")
def activate_repository(
    request: RepositoryActivationRequest
):

    repository = next(
        (
            item
            for item
            in repository_manager
            .get_saved_repositories()

            if item[
                "repository_path"
            ] == request.repository_path
        ),
        None,
    )

    if (
        repository is None
        or not os.path.isdir(
            repository[
                "repository_path"
            ]
        )
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                "That repository is not "
                "available. Import it again."
            )
        )

    try:

        repository_manager.set_repository(

            repository_name=
                repository[
                    "repository"
                ],

            repository_path=
                repository[
                    "repository_path"
                ],

            repo_url=
                repository.get(
                    "repo_url"
                ),

            files=
                repository.get(
                    "files",
                    0
                ),

            chunks=
                repository.get(
                    "chunks",
                    0
                ),
        )

        setup_active_services(
            repository[
                "repository_path"
            ]
        )

        return {
            **repository,
            "loaded": True,
        }

    except Exception as error:

        logger.exception(
            "Repository activation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# REPOSITORY STATUS
# ============================================================

@app.get("/api/repository/status")
def repository_status():

    # Do NOT automatically load on startup.
    #
    # If an endpoint asks for status, we can attempt restoration.

    if not repository_manager.is_loaded():

        auto_load_saved_repository()

    if not repository_manager.is_loaded():

        return {
            "loaded": False,
            "repository": None
        }

    return {
        "loaded": True,
        "repository":
            repository_manager.get_repository(),

        "repository_path":
            repository_manager.get_repository_path()
    }


# ============================================================
# CURRENT REPOSITORY
# ============================================================

@app.get("/api/repository")
def get_repository():

    if not repository_manager.is_loaded():

        auto_load_saved_repository()

    if not repository_manager.is_loaded():

        raise HTTPException(
            status_code=404,
            detail=(
                "No repository has been "
                "imported yet."
            )
        )

    return {
        "repository":
            repository_manager.get_repository(),

        "repository_path":
            repository_manager.get_repository_path(),

        "loaded": True
    }


# ============================================================
# REPOSITORY SUGGESTIONS
# ============================================================

@app.get("/api/repository/suggestions")
def get_repository_suggestions():

    if not repository_manager.is_loaded():

        auto_load_saved_repository()

    if not repository_manager.is_loaded():

        raise HTTPException(
            status_code=404,
            detail=(
                "Import a repository before "
                "requesting suggestions."
            )
        )

    architecture = get_architecture_service(
        repository_manager.get_repository_path()
    )

    suggestions = []

    # Feature-flow based suggestions

    for flow in architecture.get_feature_flows():

        frontend_api = (
            flow.get("frontend_api")
            or {}
        )

        route = (
            flow.get("route")
            or {}
        )

        controller = (
            flow.get("controller")
            or {}
        )

        function_name = (

            frontend_api.get(
                "function"
            )

            or flow.get(
                "name"
            )

            or controller.get(
                "controller_function"
            )
        )

        endpoint = (

            route.get(
                "path"
            )

            or frontend_api.get(
                "resolved_endpoint"
            )

            or frontend_api.get(
                "endpoint"
            )
        )

        controller_function = (
            controller.get(
                "controller_function"
            )
        )

        if function_name and endpoint:

            question = (
                f"How does "
                f"{function_name} "
                f"handle "
                f"{endpoint}"

                f"{f' through {controller_function}' if controller_function else ''}?"
            )

        elif function_name:

            question = (
                f"What does "
                f"{function_name} "
                f"do in this codebase, "
                f"and what does it depend on?"
            )

        elif endpoint:

            question = (
                f"Where is "
                f"{endpoint} "
                f"handled and what does it do?"
            )

        else:

            continue

        if question not in suggestions:

            suggestions.append(
                question
            )

        if len(suggestions) == 4:

            break

    # Fallback file-based suggestions

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
            "coverage",
            ".cache",
            "out",
            "target",

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

        repository_path = (
            repository_manager
            .get_repository_path()
        )

        for root, directories, filenames in os.walk(
            repository_path
        ):

            directories[:] = [

                directory
                for directory
                in directories

                if directory
                not in ignored_directories

            ]

            for filename in filenames:

                if (
                    os.path.splitext(
                        filename
                    )[1].lower()
                    in source_extensions
                ):

                    source_files.append(

                        os.path.relpath(

                            os.path.join(
                                root,
                                filename
                            ),

                            repository_path,

                        ).replace(
                            os.sep,
                            "/"
                        )
                    )

            if len(source_files) >= 4:

                break

        suggestions = [

            f"What is the role of "
            f"{file_path} "
            f"in this codebase?"

            for file_path
            in source_files[:4]

        ]

    return {
        "repository":
            repository_manager.get_repository(),

        "suggestions":
            suggestions,
    }

# CHAT
@app.post("/api/chat")
def chat(
    request: ChatRequest
):

    if not repository_manager.is_loaded():

        auto_load_saved_repository()

    if not repository_manager.is_loaded():

        raise HTTPException(
            status_code=400,
            detail=(
                "No repository has been "
                "imported yet."
            )
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
            "repository":
                repository_manager
                .get_repository(),

            "question":
                request.question,

            "answer":
                result["answer"],

            "sources":
                result["sources"]
        }

    except Exception as error:

        logger.exception(
            "Chat request failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ARCHITECTURE - FLOWS

@app.get("/api/architecture/flows")
def get_architecture_flows():

    if not repository_manager.is_loaded():

        auto_load_saved_repository()

    if not repository_manager.is_loaded():

        raise HTTPException(
            status_code=404,
            detail=(
                "No repository has been "
                "imported yet."
            )
        )

    architecture = get_architecture_service(
        repository_manager.get_repository_path()
    )

    try:

        flows = (
            architecture
            .get_feature_flows()
        )

        return {
            "repository":
                repository_manager
                .get_repository(),

            "flows":
                flows,

            "total":
                len(flows)
        }

    except Exception as error:

        logger.exception(
            "Architecture flow request failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# ARCHITECTURE - GRAPH
# ============================================================

@app.get("/api/architecture/graph")
def get_architecture_graph():

    if not repository_manager.is_loaded():

        auto_load_saved_repository()

    if not repository_manager.is_loaded():

        raise HTTPException(
            status_code=404,
            detail=(
                "No repository has been "
                "imported yet."
            )
        )

    architecture = get_architecture_service(
        repository_manager.get_repository_path()
    )

    try:

        graph = (
            architecture
            .get_code_graph()
        )

        return {
            "repository":
                repository_manager
                .get_repository(),

            **graph
        }

    except Exception as error:

        logger.exception(
            "Architecture graph request failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

# FILE TREE

@app.get("/api/files/tree")
def get_file_tree():

    if not repository_manager.is_loaded():

        auto_load_saved_repository()

    if not repository_manager.is_loaded():

        raise HTTPException(
            status_code=404,
            detail=(
                "No repository has been "
                "imported yet."
            )
        )

    service = get_file_service(
        repository_manager.get_repository_path()
    )

    try:

        tree = service.get_file_tree()

        return {
            "repository":
                repository_manager
                .get_repository(),

            "tree":
                tree
        }

    except Exception as error:

        logger.exception(
            "File tree request failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

# FILE CONTENT

@app.get("/api/files/content")
def get_file_content(
    path: str = Query(
        ...,
        description=(
            "Relative path to file "
            "in repository"
        )
    )
):

    if not repository_manager.is_loaded():

        auto_load_saved_repository()

    if not repository_manager.is_loaded():

        raise HTTPException(
            status_code=404,
            detail=(
                "No repository has been "
                "imported yet."
            )
        )

    service = get_file_service(
        repository_manager.get_repository_path()
    )

    try:

        content_data = (
            service.get_file_content(
                path
            )
        )

        return {
            "repository":
                repository_manager
                .get_repository(),

            **content_data
        }

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        logger.exception(
            "File content request failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )