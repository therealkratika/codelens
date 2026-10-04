from app.github.clone_repo import clone_repository
from app.ingestion.loader import load_files
from app.ingestion.chunker import chunk_documents

from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore


if __name__ == "__main__":

    repo_url = input(
        "Enter GitHub repository URL: "
    )

    repo_name = (
        repo_url
        .rstrip("/")
        .split("/")[-1]
    )

    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    # -------------------------
    # 1. Clone repository
    # -------------------------

    repo_path = clone_repository(
        repo_url,
        repo_name
    )

    # -------------------------
    # 2. Load files
    # -------------------------

    documents = load_files(
        repo_path
    )

    print(
        f"\nLoaded {len(documents)} files"
    )

    # -------------------------
    # 3. Create chunks
    # -------------------------

    chunks = chunk_documents(
        documents
    )

    print(
        f"Created {len(chunks)} chunks"
    )

    # -------------------------
    # 4. Create embeddings
    # -------------------------

    embedding_model = EmbeddingModel()

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = (
        embedding_model
        .generate_embeddings(texts)
    )

    print(
        f"Generated embeddings for "
        f"{len(embeddings)} chunks"
    )

    # -------------------------
    # 5. Store in ChromaDB
    # -------------------------

    vector_store = VectorStore()

    vector_store.add_documents(
        chunks,
        embeddings
    )

    print("\nIndexing complete! ")