import gc

from app.github.clone_repo import clone_repository
from app.ingestion.loader import load_files
from app.ingestion.chunker import chunk_documents

from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore

INDEX_BATCH_SIZE = 32


class RepositoryService:

    def __init__(self):
        print("Initializing repository service...")

        self.embedding_model = EmbeddingModel()
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

        vector_store = VectorStore(repo_path)

        # 2. Load files
        documents = load_files(
            repo_path
        )

        # 3. Create chunks
        chunks = chunk_documents(
            documents
        )

        if not chunks:
            raise ValueError(
                "No supported source files were found in this repository. "
                "CodeLens currently indexes Python, JavaScript, TypeScript, "
                "Java, C/C++, HTML, CSS, JSON, and Markdown files."
            )

        vector_store.clear()

        # Embed and persist bounded batches to avoid exhausting memory or
        # exceeding ChromaDB's per-request batch limit on larger repositories.
        try:
            for start in range(0, len(chunks), INDEX_BATCH_SIZE):
                batch = chunks[start : start + INDEX_BATCH_SIZE]
                texts = [chunk["content"] for chunk in batch]
                embeddings = self.embedding_model.generate_embeddings(texts)
                try:
                    vector_store.add_documents(
                        batch,
                        embeddings,
                        start_index=start,
                    )
                finally:
                    del texts
                    del embeddings
                    del batch
                    gc.collect()
        finally:
            self.embedding_model.model = None
            gc.collect()

        return {
            "repository": repo_name,
            "repository_path": repo_path,
            "repo_url": repo_url,
            "files": len(documents),
            "chunks": len(chunks),
            "status": "indexed"
        }