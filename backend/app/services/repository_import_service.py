import logging
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import BackgroundTasks, HTTPException

from app.github.clone_repo import validate_repository_url
from app.core.state import AppState


logger = logging.getLogger(__name__)


class RepositoryImportService:
    """Orchestrate repository import, activation, and restoration."""

    def __init__(self, state: AppState):
        self.state = state

    @property
    def repository_manager(self):
        return self.state.repository_manager

    def setup_active_services(self, repo_path: str):
        self.state.invalidate_repository_services(repo_path)

    def auto_load_saved_repository(self) -> bool:
        manager = self.repository_manager
        if manager.is_loaded():
            return True

        active_path = manager.active_repository_path
        if not active_path:
            return False

        saved_repository = next(
            (
                repository
                for repository in manager.get_saved_repositories()
                if repository.get("repository_path") == active_path
                and repository.get("repo_url")
                and os.path.isdir(repository.get("repository_path", ""))
            ),
            None,
        )

        if saved_repository is None:
            manager.active_repository_path = None
            manager._save_state()
            return False

        try:
            manager.set_repository(
                repository_name=saved_repository["repository"],
                repository_path=saved_repository["repository_path"],
                repo_url=saved_repository.get("repo_url"),
                files=saved_repository.get("files", 0),
                chunks=saved_repository.get("chunks", 0),
            )
            self.setup_active_services(saved_repository["repository_path"])
            return True
        except Exception:
            logger.exception("Failed to restore saved repository")
            return False

    def require_active_repository(self) -> str:
        if not self.repository_manager.is_loaded():
            self.auto_load_saved_repository()

        if not self.repository_manager.is_loaded():
            raise HTTPException(
                status_code=404,
                detail=(
                    "No repository is currently active. "
                    "Import or activate a repository first."
                ),
            )

        return self.repository_manager.get_repository_path()

    def perform_repository_import(self, repo_url: str) -> dict[str, Any]:
        repo_url = validate_repository_url(repo_url)
        manager = self.repository_manager
        saved_repository = manager.get_repository_by_url(repo_url)

        if (
            saved_repository
            and os.path.isdir(saved_repository.get("repository_path", ""))
        ):
            manager.set_repository(
                repository_name=saved_repository["repository"],
                repository_path=saved_repository["repository_path"],
                repo_url=saved_repository.get("repo_url"),
                files=saved_repository.get("files", 0),
                chunks=saved_repository.get("chunks", 0),
            )
            self.setup_active_services(saved_repository["repository_path"])
            return {**saved_repository, "status": "indexed"}

        result = self.state.get_repository_service().import_repository(repo_url)
        manager.set_repository(
            repository_name=result["repository"],
            repository_path=result["repository_path"],
            repo_url=result["repo_url"],
            files=result["files"],
            chunks=result["chunks"],
        )
        self.setup_active_services(result["repository_path"])
        return result

    def _update_job(self, job_id: str, **updates):
        with self.state.jobs_lock:
            job = self.state.repository_import_jobs.get(job_id)
            if job is not None:
                job.update(updates)
            return job

    def run_repository_import(self, job_id: str, repo_url: str):
        try:
            if self._update_job(job_id, status="running") is None:
                logger.error("Import job %s was not found", job_id)
                return

            result = self.perform_repository_import(repo_url)
            self._update_job(
                job_id,
                result=result,
                error=None,
                status="completed",
            )
            logger.info("Repository import completed for %s", repo_url)
        except Exception as error:
            logger.exception("Repository import failed for %s", repo_url)
            self._update_job(
                job_id,
                error=f"Repository import failed: {error}",
                status="failed",
            )
        finally:
            self.state.repository_import_lock.release()

    def start_import(
        self,
        repo_url: str,
        background_tasks: BackgroundTasks,
    ) -> dict[str, Any]:
        try:
            repo_url = validate_repository_url(repo_url)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        lock = self.state.repository_import_lock
        if not lock.acquire(blocking=False):
            raise HTTPException(
                status_code=409,
                detail=(
                    "Another repository import is already in progress. "
                    "Please wait for it to finish."
                ),
            )

        job_id = str(uuid4())
        job = {
            "job_id": job_id,
            "status": "queued",
            "result": None,
            "error": None,
        }
        with self.state.jobs_lock:
            self.state.repository_import_jobs[job_id] = job

        try:
            background_tasks.add_task(
                self.run_repository_import,
                job_id,
                repo_url,
            )
        except Exception as error:
            with self.state.jobs_lock:
                self.state.repository_import_jobs.pop(job_id, None)
            lock.release()
            logger.exception("Could not schedule import job %s", job_id)
            raise HTTPException(
                status_code=500,
                detail="Could not schedule repository import.",
            ) from error

        return dict(job)

    def get_import_status(self, job_id: str) -> dict[str, Any]:
        with self.state.jobs_lock:
            job = self.state.repository_import_jobs.get(job_id)
            if job is None:
                raise HTTPException(
                    status_code=404,
                    detail="Repository import job was not found.",
                )
            return dict(job)
