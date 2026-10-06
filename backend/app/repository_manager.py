from app.rag.rag_pipeline import RAGPipeline


class RepositoryManager:

    def __init__(self):
        self.current_repository = None
        self.repository_path = None
        self.rag_pipeline = None

    def set_repository(self, repository_name, repository_path):
        print(f"Initializing RAG for repository: {repository_name}")

        self.current_repository = repository_name
        self.repository_path = repository_path

        self.rag_pipeline = RAGPipeline(
            repository_path
        )

        print(
            f"Repository '{repository_name}' is now active."
        )

    def is_loaded(self):
        return self.rag_pipeline is not None

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