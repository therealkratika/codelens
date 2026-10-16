import logging
import os
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.config import BACKEND_ROOT
from app.core.state import app_state
from app.github.clone_repo import clone_repository
from app.repository_storage import save_repository
from app.schemas.repository import (
    RepositoryActivationRequest,
    RepositoryImportRequest,
)
from app.services.repository_import_service import RepositoryImportService


logger = logging.getLogger(__name__)
router = APIRouter()
import_service = RepositoryImportService(app_state)


@router.post("/api/repository/import", status_code=202)
def import_repository(
    request: RepositoryImportRequest,
    background_tasks: BackgroundTasks,
):
    return import_service.start_import(request.repo_url, background_tasks)


@router.get("/api/repository/import/{job_id}")
def get_repository_import_status(job_id: str):
    return import_service.get_import_status(job_id)


@router.get("/api/repository/saved")
def get_saved_repositories():
    manager = app_state.repository_manager
    return {
        "repositories": manager.get_saved_repositories(),
        "active_repository_path": manager.active_repository_path,
    }


@router.post("/api/repository/activate")
@router.post("/repository/activate")
def activate_repository(request: RepositoryActivationRequest):
    manager = app_state.repository_manager
    req_path = request.repository_path
    req_folder = Path(req_path).name
    repository = next(
        (
            item
            for item in manager.get_saved_repositories()
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
        save_repository(repository)
    elif repository.get("repo_url"):
        try:
            target_path = clone_repository(
                repository["repo_url"],
                repository.get("repository", folder_name),
            )
            repository["repository_path"] = target_path
            save_repository(repository)
        except Exception as error:
            logger.exception("Failed to auto-clone repository on activation")
            raise HTTPException(
                status_code=500,
                detail=(
                    "Could not restore repository files on server. "
                    "Import it again."
                ),
            ) from error
    else:
        raise HTTPException(
            status_code=404,
            detail="That repository is unavailable. Import it again.",
        )

    try:
        manager.set_repository(
            repository_name=repository["repository"],
            repository_path=target_path,
            repo_url=repository.get("repo_url"),
            files=repository.get("files", 0),
            chunks=repository.get("chunks", 0),
        )
        import_service.setup_active_services(target_path)
        return {**repository, "repository_path": target_path, "loaded": True}
    except Exception as error:
        logger.exception("Repository activation failed")
        raise HTTPException(
            status_code=500,
            detail="Repository activation failed. Check the backend logs.",
        ) from error


@router.get("/api/repository/status")
def repository_status():
    manager = app_state.repository_manager
    if not manager.is_loaded():
        import_service.auto_load_saved_repository()
    if not manager.is_loaded():
        return {"loaded": False, "repository": None}
    return {
        "loaded": True,
        "repository": manager.get_repository(),
        "repository_path": manager.get_repository_path(),
    }


@router.get("/api/repository")
def get_repository():
    manager = app_state.repository_manager
    repo_path = import_service.require_active_repository()
    return {
        "repository": manager.get_repository(),
        "repository_path": repo_path,
        "loaded": True,
    }


@router.get("/api/repository/suggestions")
def get_repository_suggestions():
    manager = app_state.repository_manager
    repo_path = import_service.require_active_repository()
    architecture = app_state.get_architecture_service(repo_path)
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
            controller_function = controller.get("controller_function")
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
                question = f"Where is {endpoint} handled and what does it do?"
            else:
                continue
            if question not in suggestions:
                suggestions.append(question)
            if len(suggestions) >= 4:
                break

        if not suggestions:
            ignored_directories = {
                ".git", "node_modules", "venv", ".venv", "__pycache__",
                "dist", "build", ".next", "coverage", ".cache", "out", "target",
            }
            source_extensions = {
                ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs",
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
                                os.path.join(root, filename), repo_path,
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
        return {"repository": manager.get_repository(), "suggestions": suggestions}
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Repository suggestions failed")
        raise HTTPException(
            status_code=500,
            detail="Could not generate repository suggestions.",
        ) from error
