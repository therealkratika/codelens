import gc
from itertools import islice

from app.github.clone_repo import clone_repository
from app.ingestion.loader import iter_files
from app.ingestion.chunker import iter_document_chunks

from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore

INDEX_BATCH_SIZE = 64


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

        # Stream files and chunks so indexing does not retain multiple
        # repository-wide copies of source text in memory.
        file_count = 0

        def counted_files():
            nonlocal file_count
            for document in iter_files(repo_path):
                file_count += 1
                yield document

        chunks = iter_document_chunks(counted_files())
        batch = list(islice(chunks, INDEX_BATCH_SIZE))
        if not batch:
            raise ValueError(
                "No supported source files were found in this repository. "
                "CodeLens currently indexes Python, JavaScript, TypeScript, "
                "Java, C/C++, HTML, CSS, JSON, and Markdown files."
            )

        vector_store.clear()
        chunk_count = 0

        # Larger bounded batches reduce inference and ChromaDB write overhead.
        try:
            while batch:
                texts = [chunk["content"] for chunk in batch]
                embeddings = self.embedding_model.generate_embeddings(texts)
                try:
                    vector_store.add_documents(
                        batch,
                        embeddings,
                        start_index=chunk_count,
                    )
                    chunk_count += len(batch)
                finally:
                    del texts
                    del embeddings
                    del batch
                batch = list(islice(chunks, INDEX_BATCH_SIZE))
        finally:
            self.embedding_model.model = None
            gc.collect()

        return {
            "repository": repo_name,
            "repository_path": repo_path,
            "repo_url": repo_url,
            "files": file_count,
            "chunks": chunk_count,
            "status": "indexed"
        }