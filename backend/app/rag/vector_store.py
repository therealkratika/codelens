import hashlib
from pathlib import Path

import chromadb


class VectorStore:

    def __init__(self, repository_path=None):
        backend_root = Path(__file__).resolve().parents[2]

        self.client = chromadb.PersistentClient(
            path=str(backend_root / "chroma_db")
        )

        collection_name = "codebase"
        if repository_path is not None:
            resolved_path = Path(repository_path).resolve()
            legacy_default = (
                resolved_path.name.lower() == "nextja_coding_battle"
                and "codebase" in {
                    collection.name
                    for collection in self.client.list_collections()
                }
            )
            if not legacy_default:
                path_hash = hashlib.sha1(
                    str(resolved_path).encode("utf-8")
                ).hexdigest()[:16]
                collection_name = f"codebase_{path_hash}"

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_documents(
        self,
        chunks,
        embeddings,
        start_index=0,
    ):

        documents = []
        metadatas = []
        ids = []

        for offset, chunk in enumerate(chunks):
            index = start_index + offset

            documents.append(
                chunk["content"]
            )

            metadatas.append({
                "file": chunk["file"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"]
            })

            ids.append(
                f"chunk_{index}"
            )

        self.collection.upsert(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )

        print(
            f"Stored {len(chunks)} chunks in ChromaDB"
        )

    def clear(self):
        existing_ids = self.collection.get(include=[])["ids"]
        if existing_ids:
            self.collection.delete(ids=existing_ids)

    def search(
        self,
        query_embedding,
        top_k=5
    ):

        results = self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=top_k
        )

        return results