
import hashlib
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv


backend_root = Path(__file__).resolve().parents[2]
load_dotenv(backend_root / ".env")


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

        collection_name = "codebase"

        if repository_path is not None:
            resolved_path = Path(repository_path).resolve()

            collections = self.client.list_collections()
            collection_names = {
                item if isinstance(item, str) else item.name
                for item in collections
            }

            legacy_default = (
                resolved_path.name.lower() == "nextja_coding_battle"
                and "codebase" in collection_names
            )

            if not legacy_default:
                path_hash = hashlib.sha1(
                    str(resolved_path).encode("utf-8")
                ).hexdigest()[:16]

                collection_name = f"codebase_{path_hash}"

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

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )

        return results
