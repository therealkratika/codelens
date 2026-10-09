import hashlib
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv


backend_root = Path(__file__).resolve().parents[2]
load_dotenv(backend_root / ".env")


def get_collection_name(repository_path=None):
    """Return a stable collection name for a repository."""
    if repository_path is None:
        return "codebase"

    resolved_path = Path(repository_path).resolve()

    # clone_repo.py creates checkout folders as:
    # <safe_repository_name>_<sha1_of_repository_url>
    # The URL hash stays stable even if the checkout's absolute
    # directory changes between deployments.
    folder_name = resolved_path.name
    suffix = folder_name.rsplit("_", 1)[-1]

    if len(suffix) == 10 and all(
        char in "0123456789abcdef" for char in suffix.lower()
    ):
        stable_id = suffix
    else:
        # Fallback for repositories that were not cloned by clone_repo.py.
        stable_id = hashlib.sha1(
            str(resolved_path).encode("utf-8")
        ).hexdigest()[:16]

    return f"codebase_{stable_id}"


class VectorStore:
    def __init__(self, repository_path=None):
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT")
        database = os.getenv("CHROMA_DATABASE", "codelens")

        if api_key:
            if not tenant:
                raise ValueError(
                    "CHROMA_TENANT is required when using Chroma Cloud."
                )

            self.client = chromadb.CloudClient(
                api_key=api_key,
                tenant=tenant,
                database=database,
            )
            print("Connected to Chroma Cloud.")
        else:
            self.client = chromadb.PersistentClient(
                path=str(backend_root / "chroma_db")
            )
            print("Using local ChromaDB.")

        collection_name = get_collection_name(repository_path)

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        print(f"Using collection: {collection_name}")

    def add_documents(self, chunks, embeddings, start_index=0):
        if not chunks:
            return

        documents = []
        metadatas = []
        ids = []

        for offset, chunk in enumerate(chunks):
            index = start_index + offset

            documents.append(chunk["content"])
            metadatas.append({
                "file": chunk["file"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
            })
            ids.append(f"chunk_{index}")

        embedding_list = (
            embeddings.tolist()
            if hasattr(embeddings, "tolist")
            else embeddings
        )

        self.collection.upsert(
            documents=documents,
            embeddings=embedding_list,
            metadatas=metadatas,
            ids=ids,
        )

        print(f"Stored {len(chunks)} chunks in ChromaDB")

    def clear(self):
        existing_ids = self.collection.get(include=[])["ids"]

        if existing_ids:
            self.collection.delete(ids=existing_ids)

    def search(self, query_embedding, top_k=5):
        embedding = (
            query_embedding.tolist()
            if hasattr(query_embedding, "tolist")
            else query_embedding
        )

        return self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )