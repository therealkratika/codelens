
from app.repository_storage import (
    get_saved_repositories as fetch_saved_repositories,
    get_repository_by_url as fetch_repository_by_url,
    get_active_repository_path,
    save_repository,
    set_active_repository,
)


class RepositoryManager:
    def __init__(self):
        self.current_repository = None
        self.repository_path = None
        self.rag_pipeline = None

        self.repositories = []

        # Restore the active repository path from MongoDB.
        try:
            self.active_repository_path = get_active_repository_path()
        except Exception as error:
            print(f"Could not load active repository: {error}")
            self.active_repository_path = None

        # Load saved repository metadata from MongoDB.
        self._load_saved_repositories()

    def _load_saved_repositories(self):
        try:
            self.repositories = fetch_saved_repositories()
        except Exception as error:
            print(f"Could not load repositories from MongoDB: {error}")
            self.repositories = []

    def _save_state(self):
        """Refresh the in-memory repository list from MongoDB."""
        self._load_saved_repositories()

    def get_saved_repositories(self):
        self._load_saved_repositories()
        return list(self.repositories)

    def get_repository_by_url(self, repo_url):
        return fetch_repository_by_url(repo_url)

    def set_repository(
        self,
        repository_name,
        repository_path,
        repo_url=None,
        files=0,
        chunks=0,
        load_rag=False,
    ):
        print(f"Activating repository: {repository_name}")

        # Preserve lazy initialization to limit memory usage.
        rag_pipeline = None

        if load_rag:
            print("Loading RAG pipeline...")
            from app.rag.rag_pipeline import RAGPipeline

            rag_pipeline = RAGPipeline(repository_path)

        # Reuse existing metadata when optional values are omitted.
        existing = None

        if repo_url:
            existing = fetch_repository_by_url(repo_url)

        existing = existing or {}

        resolved_repo_url = repo_url or existing.get("repo_url")

        repository = {
            "repository": repository_name,
            "repository_path": repository_path,
            "repo_url": resolved_repo_url,
            "files": (
                files
                if files
                else existing.get("files", 0)
            ),
            "chunks": (
                chunks
                if chunks
                else existing.get("chunks", 0)
            ),
            "status": "indexed",
        }

        # Persist repository metadata when its URL is known.
        if resolved_repo_url:
            save_repository(repository)

        # Update the active repository in memory.
        self.current_repository = repository_name
        self.repository_path = repository_path
        self.rag_pipeline = rag_pipeline
        self.active_repository_path = repository_path

        # Persist active selection separately in MongoDB.
        set_active_repository(repository_path)

        self._load_saved_repositories()

        print(f"Repository '{repository_name}' is now active.")

    def get_rag_pipeline(self):
        if self.rag_pipeline is None:
            if not self.repository_path:
                raise RuntimeError("No repository is active.")

            print("Initializing RAG pipeline...")

            from app.rag.rag_pipeline import RAGPipeline

            self.rag_pipeline = RAGPipeline(self.repository_path)

            print("RAG pipeline initialized.")

        return self.rag_pipeline

    def is_loaded(self):
        return self.repository_path is not None

    def is_rag_loaded(self):
        return self.rag_pipeline is not None

    def get_repository(self):
        return self.current_repository

    def get_repository_path(self):
        return self.repository_path

    def clear(self):
        """Clear the active selection without deleting saved repositories."""
        self.current_repository = None
        self.repository_path = None
        self.rag_pipeline = None
        self.active_repository_path = None

        set_active_repository(None)

        print("Active repository cleared.")

