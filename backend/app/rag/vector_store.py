import chromadb


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="codebase"
        )

    def add_documents(
        self,
        chunks,
        embeddings
    ):

        documents = []
        metadatas = []
        ids = []

        for index, chunk in enumerate(chunks):

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

        self.collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )

        print(
            f"Stored {len(chunks)} chunks in ChromaDB"
        )

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