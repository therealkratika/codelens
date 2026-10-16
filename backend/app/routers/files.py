import logging

from fastapi import APIRouter, HTTPException, Query

from app.core.state import app_state
from app.services.repository_import_service import RepositoryImportService


logger = logging.getLogger(__name__)
router = APIRouter()
import_service = RepositoryImportService(app_state)


@router.get("/api/files/tree")
def get_file_tree():
    manager = app_state.repository_manager
    repo_path = import_service.require_active_repository()
    try:
        tree = app_state.get_file_service(repo_path).get_file_tree()
        return {"repository": manager.get_repository(), "tree": tree}
    except Exception as error:
        logger.exception("File tree request failed")
        raise HTTPException(
            status_code=500,
            detail="Could not load the file tree.",
        ) from error


@router.get("/api/files/content")
def get_file_content(
    path: str = Query(
        ...,
        min_length=1,
        description="Relative path to a file in the active repository",
    ),
):
    manager = app_state.repository_manager
    repo_path = import_service.require_active_repository()
    try:
        content_data = app_state.get_file_service(repo_path).get_file_content(path)
        return {"repository": manager.get_repository(), **content_data}
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="File was not found in the active repository.",
        ) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.exception("File content request failed")
        raise HTTPException(
            status_code=500,
            detail="Could not read the requested file.",
        ) from error
