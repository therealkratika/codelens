import logging
from threading import Lock, RLock
from typing import Any

from app.repository_manager import RepositoryManager


logger = logging.getLogger(__name__)


class AppState:
    """Process-local state shared by all API routers."""

    def __init__(self):
        self.repository_manager = RepositoryManager()
        self.repository_import_lock = Lock()
        self.repository_import_jobs: dict[str, dict[str, Any]] = {}
        self.jobs_lock = RLock()

        self.repository_service = None
        self.architecture_service = None
        self.file_service = None

    def get_repository_service(self):
        if self.repository_service is None:
            from app.repository_service import RepositoryService

            self.repository_service = RepositoryService()
        return self.repository_service

    def get_architecture_service(self, repo_path: str):
        if (
            self.architecture_service is None
            or self.architecture_service.repository_path != repo_path
        ):
            from app.architecture_service import ArchitectureService

            self.architecture_service = ArchitectureService(repo_path)
        return self.architecture_service

    def get_file_service(self, repo_path: str):
        if (
            self.file_service is None
            or self.file_service.repository_path != repo_path
        ):
            from app.file_service import FileService

            self.file_service = FileService(repo_path)
        return self.file_service

    def invalidate_repository_services(self, repo_path: str):
        self.architecture_service = None
        self.file_service = None
        logger.info("Active repository changed to: %s", repo_path)


app_state = AppState()
