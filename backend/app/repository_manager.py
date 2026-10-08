import json
from pathlib import Path


class RepositoryManager:

    def __init__(self):
        self.current_repository = None
        self.repository_path = None
        self.rag_pipeline = None

        self.state_path = (
            Path(__file__).resolve().parents[1]
            / "repository_state.json"
        )

        self.repositories = []
        self.active_repository_path = None

        if self.state_path.exists():
            state = json.loads(
                self.state_path.read_text(
                    encoding="utf-8"
                )
            )

            self.repositories = state.get(
                "repositories",
                []
            )

            self.active_repository_path = state.get(
                "active_repository_path"
            )

    def _save_state(self):

        self.state_path.write_text(
            json.dumps(
                {
                    "repositories": self.repositories,
                    "active_repository_path":
                        self.active_repository_path,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def get_saved_repositories(self):

        return list(
            self.repositories
        )

    def get_repository_by_url(
        self,
        repo_url
    ):

        normalized_url = (
            repo_url
            .rstrip("/")
            .removesuffix(".git")
            .lower()
        )

        return next(
            (
                repository
                for repository in self.repositories
                if (
                    repository.get("repo_url") or ""
                )
                .rstrip("/")
                .removesuffix(".git")
                .lower()
                == normalized_url
            ),
            None,
        )

    def set_repository(
        self,
        repository_name,
        repository_path,
        repo_url=None,
        files=0,
        chunks=0,
    ):

        print(
            f"Initializing RAG for repository: "
            f"{repository_name}"
        )

        # IMPORTANT:
        # Import RAGPipeline only when a repository
        # actually needs to be loaded.
        from app.rag.rag_pipeline import RAGPipeline

        rag_pipeline = RAGPipeline(
            repository_path
        )

        repository = next(
            (
                item
                for item in self.repositories
                if item["repository_path"]
                == repository_path
            ),
            {},
        )

        repository.update(
            {
                "repository":
                    repository_name,

                "repository_path":
                    repository_path,

                "repo_url":
                    repo_url
                    or repository.get(
                        "repo_url"
                    ),

                "files":
                    files
                    or repository.get(
                        "files",
                        0
                    ),

                "chunks":
                    chunks
                    or repository.get(
                        "chunks",
                        0
                    ),
            }
        )

        self.repositories = [
            item
            for item in self.repositories
            if item["repository_path"]
            != repository_path
        ]

        self.repositories.append(
            repository
        )

        self.current_repository = (
            repository_name
        )

        self.repository_path = (
            repository_path
        )

        self.rag_pipeline = (
            rag_pipeline
        )

        self.active_repository_path = (
            repository_path
        )

        self._save_state()

        print(
            f"Repository "
            f"'{repository_name}' "
            f"is now active."
        )

    def is_loaded(self):

        return (
            self.rag_pipeline
            is not None
        )

    def get_repository(self):

        return self.current_repository

    def get_repository_path(self):

        return self.repository_path

    def get_rag_pipeline(self):

        return self.rag_pipeline

    def clear(self):

        self.current_repository = None
        self.repository_path = None
        self.rag_pipeline = None