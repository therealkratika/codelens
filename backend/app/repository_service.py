from app.github.clone_repo import clone_repository
from app.ingestion.loader import load_files
from app.ingestion.chunker import chunk_documents

from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore


class RepositoryService:

    def __init__(self):
        print("Initializing repository service...")

        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()

        print("Repository service ready!")

    def import_repository(self, repo_url: str):

        repo_name = (
            repo_url
            .rstrip("/")
            .split("/")[-1]
        )

        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        # 1. Clone repository
        repo_path = clone_repository(
            repo_url,
            repo_name
        )

        # 2. Load files
        documents = load_files(
            repo_path
        )

        # 3. Create chunks
        chunks = chunk_documents(
            documents
        )

        # 4. Generate embeddings
        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_model
            .generate_embeddings(texts)
        )

        # 5. Store in ChromaDB
        self.vector_store.add_documents(
            chunks,
            embeddings
        )

        return {
            "repository": repo_name,
            "repository_path": repo_path,
            "files": len(documents),
            "chunks": len(chunks),
            "status": "indexed"
        }