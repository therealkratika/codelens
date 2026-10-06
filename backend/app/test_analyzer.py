import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    backend_root = Path(__file__).resolve().parent.parent
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

from collections import defaultdict

from app.rag.retriever import Retriever
from app.rag.code_analyzer import CodeAnalyzer


def main():

    retriever = Retriever()

    analyzer = CodeAnalyzer()

    data = retriever.vector_store.collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    documents = data["documents"]
    metadatas = data["metadatas"]

    # -------------------------------------------------
    # GROUP CHUNKS BY FILE
    # -------------------------------------------------

    files = defaultdict(list)

    for document, metadata in zip(
        documents,
        metadatas
    ):

        file_path = metadata["file"]

        files[file_path].append({
            "document": document,
            "metadata": metadata
        })

    print("\n" + "=" * 70)
    print("CODEBASE AST ANALYSIS")
    print("=" * 70)

    print(
        f"\nFiles found: {len(files)}"
    )

    # -------------------------------------------------
    # RECONSTRUCT AND ANALYZE EACH FILE
    # -------------------------------------------------

    for file_path, chunks in files.items():

        extension = (
            file_path.split(".")[-1]
            .lower()
        )

        if extension not in {
            "js",
            "jsx",
            "ts",
            "tsx"
        }:
            continue

        # Sort chunks by starting line
        chunks.sort(
            key=lambda x:
            x["metadata"]["start_line"]
        )

        # Reconstruct file
        full_code = "\n".join(
            chunk["document"]
            for chunk in chunks
        )

        result = analyzer.analyze_file(
            file_path,
            full_code
        )

        if not (
            result["imports"]
            or result["functions"]
            or result["calls"]
        ):
            continue

        print("\n" + "-" * 70)

        print(
            f"FILE: {file_path}"
        )

        print("\nIMPORTS:")

        for item in result["imports"]:
            print(f"  → {item}")

        print("\nFUNCTIONS:")

        for function in result["functions"]:

            print(
                f"  → {function['name']} "
                f"({function['start_line']}-"
                f"{function['end_line']})"
            )

        print("\nCALLS:")

        for call in result["calls"][:20]:

            print(
                f"  → {call['name']} "
                f"(line {call['start_line']})"
            )


if __name__ == "__main__":
    main()