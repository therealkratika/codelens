
import logging
from pathlib import Path
from threading import RLock

from app.repository_storage import (
    get_saved_repositories as fetch_saved_repositories,
    get_repository_by_url as fetch_repository_by_url,
    get_active_repository_path,
    save_repository,
    set_active_repository,
)

logger = logging.getLogger(__name__)


class RepositoryManager:
    def __init__(self):
        self.current_repository = None
        self.repository_path = None
        self.rag_pipeline = None
        self.repositories = []

        # Protect changes to the active repository and pipeline.
        self._lock = RLock()

        try:
            self.active_repository_path = get_active_repository_path()
        except Exception:
            logger.exception("Could not load active repository from storage")
            self.active_repository_path = None

        self._load_saved_repositories()
        self._restore_active_repository()

    # REPOSITORY STORAGE

    def _load_saved_repositories(self):
        try:
            self.repositories = fetch_saved_repositories() or []
        except Exception:
            logger.exception("Could not load saved repositories")
            self.repositories = []

    def _save_state(self):
        """Refresh the in-memory repository metadata from MongoDB."""
        self._load_saved_repositories()

    def get_saved_repositories(self):
        self._load_saved_repositories()
        return list(self.repositories)

    def get_repository_by_url(self, repo_url):
        return fetch_repository_by_url(repo_url)

    def _restore_active_repository(self):
        """
        Restore repository metadata for the saved active path.
        Do not initialize the RAG pipeline until it is needed.
        """
        if not self.active_repository_path:
            return

        active_path = Path(self.active_repository_path).expanduser()

        if not active_path.is_dir():
            logger.warning(
                "Saved active repository path does not exist: %s",
                active_path,
            )
            self.active_repository_path = None
            return

        resolved_path = str(active_path.resolve())

        repository = next(
            (
                item
                for item in self.repositories
                if item.get("repository_path")
                and str(
                    Path(item["repository_path"]).expanduser().resolve()
                ) == resolved_path
            ),
            None,
        )

        if repository is None:
            logger.warning(
                "No saved repository metadata found for active path: %s",
                resolved_path,
            )
            return

        self.current_repository = repository.get("repository")
        self.repository_path = resolved_path
        self.active_repository_path = resolved_path

    # ACTIVATE REPOSITORY

    def set_repository(
        self,
        repository_name,
        repository_path,
        repo_url=None,
        files=0,
        chunks=0,
        load_rag=False,
    ):
        """
        Activate a repository and invalidate any previous
        repository's cached RAG pipeline.
        """
        if not repository_path:
            raise ValueError("Repository path cannot be empty.")

        path = Path(repository_path).expanduser().resolve()

        if not path.is_dir():
            raise FileNotFoundError(
                f"Repository directory does not exist: {path}"
            )

        resolved_path = str(path)

        with self._lock:
            logger.info("Activating repository: %s", repository_name)

            # Resolve missing metadata without losing valid saved values.
            existing = None

            if repo_url:
                existing = fetch_repository_by_url(repo_url)

            if existing is None:
                existing = next(
                    (
                        item
                        for item in self.get_saved_repositories()
                        if str(
                            Path(
                                item.get("repository_path", "")
                            ).expanduser().resolve()
                        ) == resolved_path
                    ),
                    {},
                )

            existing = existing or {}

            repository = {
                "repository": repository_name,
                "repository_path": resolved_path,
                "repo_url": repo_url or existing.get("repo_url"),
                "files": (
                    files
                    if files is not None and files != 0
                    else existing.get("files", 0)
                ),
                "chunks": (
                    chunks
                    if chunks is not None and chunks != 0
                    else existing.get("chunks", 0)
                ),
                "status": "indexed",
            }

            # Persist metadata before changing active in-memory state.
            if repository["repo_url"]:
                save_repository(repository)

            set_active_repository(resolved_path)

            # Clear the old pipeline whenever the repository changes.
            repository_changed = self.repository_path != resolved_path

            if repository_changed:
                self.rag_pipeline = None

            self.current_repository = repository_name
            self.repository_path = resolved_path
            self.active_repository_path = resolved_path

            self._load_saved_repositories()

            # Optional eager initialization.
            if load_rag:
                self.rag_pipeline = self._create_rag_pipeline(
                    resolved_path
                )

            logger.info(
                "Repository '%s' is active at %s",
                repository_name,
                resolved_path,
            )

    # RAG PIPELINE

    @staticmethod
    def _create_rag_pipeline(repository_path):
        """Construct a pipeline scoped to a specific repository."""
        from app.rag.rag_pipeline import RAGPipeline

        return RAGPipeline(repository_path)

    def get_rag_pipeline(self):
        """
        Return the pipeline for the active repository.
        Rebuild it if it belongs to a different repository.
        """
        with self._lock:
            if not self.repository_path:
                raise RuntimeError("No repository is active.")

            active_path = str(
                Path(self.repository_path).expanduser().resolve()
            )

            if not Path(active_path).is_dir():
                raise FileNotFoundError(
                    f"Active repository directory does not exist: "
                    f"{active_path}"
                )

            pipeline_path = getattr(
                self.rag_pipeline,
                "repository_path",
                None,
            )

            if (
                self.rag_pipeline is None
                or (
                    pipeline_path is not None
                    and str(Path(pipeline_path).expanduser().resolve())
                    != active_path
                )
            ):
                logger.info(
                    "Initializing RAG pipeline for %s",
                    active_path,
                )

                self.rag_pipeline = self._create_rag_pipeline(
                    active_path
                )

            return self.rag_pipeline

    # STATUS

    def is_loaded(self):
        return bool(self.repository_path)

    def is_rag_loaded(self):
        return self.rag_pipeline is not None

    def get_repository(self):
        return self.current_repository

    def get_repository_path(self):
        return self.repository_path
    # CLEAR ACTIVE REPOSITORY
    def clear(self):
        """
        Clear the active selection without deleting saved repositories.
        """
        with self._lock:
            set_active_repository(None)

            self.current_repository = None
            self.repository_path = None
            self.rag_pipeline = None
            self.active_repository_path = None

            logger.info("Active repository cleared")
