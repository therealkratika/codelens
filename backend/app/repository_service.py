import gc
import logging
from itertools import islice
from pathlib import Path
from urllib.parse import urlparse

from app.github.clone_repo import clone_repository
from app.ingestion.loader import iter_files
from app.ingestion.chunker import iter_document_chunks
from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore
from app.repository_storage import save_repository

logger = logging.getLogger(__name__)

INDEX_BATCH_SIZE = 8


class RepositoryService:
    def __init__(self):
        # Initialize lazily so importing this service does not
        # immediately load a large embedding model into memory.
        self.embedding_model = None

    def _get_embedding_model(self):
        """
        Create the embedding model when needed.
        Recreate it if a previous indexing operation released it.
        """
        if (
            self.embedding_model is None
            or getattr(self.embedding_model, "model", None) is None
        ):
            logger.info("Initializing embedding model")
            self.embedding_model = EmbeddingModel()

        return self.embedding_model

    @staticmethod
    def _get_repository_name(repo_url: str) -> str:
        """Extract a repository name from a Git URL."""
        parsed = urlparse(repo_url)
        path = parsed.path.rstrip("/")

        name = Path(path).name

        if name.endswith(".git"):
            name = name[:-4]

        if not name:
            raise ValueError("Could not determine repository name from URL.")

        # Avoid accepting arbitrary path characters as a folder name.
        if name in {".", ".."} or "/" in name or "\\" in name:
            raise ValueError("Invalid repository name.")

        return name

    def import_repository(self, repo_url: str):
        repo_url = repo_url.strip()

        if not repo_url:
            raise ValueError("Repository URL cannot be empty.")

        repo_name = self._get_repository_name(repo_url)

        logger.info("Importing repository: %s", repo_url)

        # 1. Clone or locate the local repository.
        repo_path = str(
            Path(clone_repository(repo_url, repo_name)).resolve()
        )

        if not Path(repo_path).is_dir():
            raise FileNotFoundError(
                f"Repository directory does not exist: {repo_path}"
            )

        # 2. Get a repository-specific vector store.
        vector_store = VectorStore(repo_path)

        file_count = 0

        def counted_files():
            nonlocal file_count

            for document in iter_files(repo_path):
                file_count += 1
                yield document

        chunks = iter_document_chunks(counted_files())

        chunk_count = 0
        batch = list(islice(chunks, INDEX_BATCH_SIZE))

        if not batch:
            raise ValueError(
                "No supported source files were found in this repository. "
                "Check the repository contents and the file extensions "
                "supported by the ingestion loader."
            )

        # 3. Index documents in small batches.
        #
        # NOTE: This assumes VectorStore.clear() clears only the
        # collection associated with repo_path. Verify that behavior
        # in vector_store.py before relying on repository isolation.
        vector_store.clear()

        try:
            while batch:
                texts = [chunk["content"] for chunk in batch]

                try:
                    embedding_model = self._get_embedding_model()
                    embeddings = embedding_model.generate_embeddings(texts)

                    vector_store.add_documents(
                        batch,
                        embeddings,
                        start_index=chunk_count,
                    )

                    chunk_count += len(batch)

                finally:
                    if "texts" in locals():
                        del texts

                    if "embeddings" in locals():
                        del embeddings

                    gc.collect()

                batch = list(islice(chunks, INDEX_BATCH_SIZE))

            if chunk_count == 0:
                raise ValueError(
                    "Indexing completed without adding any chunks."
                )

            result = {
                "repository": repo_name,
                "repository_path": repo_path,
                "repo_url": repo_url,
                "files": file_count,
                "chunks": chunk_count,
                "status": "indexed",
            }

            # 4. Save metadata only after indexing succeeds.
            save_repository(result)

            logger.info(
                "Repository indexed successfully: %s files, %s chunks",
                file_count,
                chunk_count,
            )

            return result

        except Exception:
            logger.exception(
                "Failed to index repository %s",
                repo_url,
            )
            raise

        finally:
            # Release the large model after this import.
            if self.embedding_model is not None:
                self.embedding_model.model = None
                self.embedding_model = None

            gc.collect()
