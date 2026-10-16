import logging

from fastapi import APIRouter, HTTPException

from app.core.state import app_state
from app.services.repository_import_service import RepositoryImportService


logger = logging.getLogger(__name__)
router = APIRouter()
import_service = RepositoryImportService(app_state)


@router.get("/api/architecture/flows")
def get_architecture_flows():
    manager = app_state.repository_manager
    repo_path = import_service.require_active_repository()
    try:
        flows = app_state.get_architecture_service(repo_path).get_feature_flows()
        return {
            "repository": manager.get_repository(),
            "flows": flows,
            "total": len(flows),
        }
    except Exception as error:
        logger.exception("Architecture flow request failed")
        raise HTTPException(
            status_code=500,
            detail="Could not load architecture flows.",
        ) from error


@router.get("/api/architecture/graph")
def get_architecture_graph():
    manager = app_state.repository_manager
    repo_path = import_service.require_active_repository()
    try:
        graph = app_state.get_architecture_service(repo_path).get_code_graph()
        return {"repository": manager.get_repository(), **graph}
    except Exception as error:
        logger.exception("Architecture graph request failed")
        raise HTTPException(
            status_code=500,
            detail="Could not load the architecture graph.",
        ) from error
