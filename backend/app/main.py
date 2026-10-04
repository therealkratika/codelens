from github.clone_repo import clone_repository
from ingestion.loader import load_files
from ingestion.chunker import chunk_documents


if __name__ == "__main__":

    repo_url = input("Enter GitHub repository URL: ")

    repo_name = repo_url.rstrip("/").split("/")[-1]

    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    # 1. Clone
    repo_path = clone_repository(
        repo_url,
        repo_name
    )

    # 2. Load files
    documents = load_files(repo_path)

    print(f"\nLoaded {len(documents)} files")

    # 3. Chunk
    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks\n")

    # Show first 5 chunks

    for chunk in chunks[:5]:

        print("=" * 60)

        print(
            f"File: {chunk['file']}"
        )

        print(
            f"Lines: "
            f"{chunk['start_line']}-"
            f"{chunk['end_line']}"
        )

        print()

        print(chunk["content"][:500])