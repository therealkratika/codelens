import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    backend_root = Path(__file__).resolve().parent.parent
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

from pathlib import Path

from app.rag.api_flow_analyzer import APIFlowAnalyzer
from app.rag.vector_store import VectorStore


analyzer = APIFlowAnalyzer()
vector_store = VectorStore()


data = vector_store.collection.get(
    include=["documents", "metadatas"]
)

documents = data["documents"]
metadatas = data["metadatas"]


print("=" * 70)
print("API FILE DEBUG")
print("=" * 70)

print("Total chunks:", len(documents))


# Show all files containing "api"
api_files = set()

for metadata in metadatas:

    file_path = metadata["file"]

    if "api" in file_path.lower():
        api_files.add(file_path)


print("\nFiles containing 'api':")

for file_path in sorted(api_files):
    print("→", file_path)


# Find exact frontend/lib/api.ts chunks
chunks = []

for document, metadata in zip(documents, metadatas):

    if metadata["file"] == "frontend/lib/api.ts":

        chunks.append({
            "document": document,
            "start_line": metadata["start_line"],
            "end_line": metadata["end_line"]
        })


print("\nMatching chunks:", len(chunks))


for chunk in chunks:

    print(
        f"\nChunk lines "
        f"{chunk['start_line']}-{chunk['end_line']}"
    )

    print(chunk["document"][:500])


if not chunks:

    print("\n❌ frontend/lib/api.ts was NOT found in Chroma.")

else:

    chunks.sort(
        key=lambda x: x["start_line"]
    )

    api_file = (
        Path(__file__).resolve().parents[1]
        / "repositories"
        / "Nextja_coding_battle"
        / "frontend"
        / "lib"
        / "api.ts"
    )
    full_code = api_file.read_text(encoding="utf-8")

    print("\n" + "=" * 70)
    print("RUNNING API ANALYZER")
    print("=" * 70)

    results = analyzer.analyze(
        "frontend/lib/api.ts",
        full_code
    )

    print("\nBASE ENDPOINTS")
    print("-" * 70)

    base_endpoints = analyzer.extract_base_endpoints(
        full_code
    )

    for name, value in base_endpoints.items():
        print(f"{name} → {value}")

    print("\nResults:")

    for result in results:
        print(result)