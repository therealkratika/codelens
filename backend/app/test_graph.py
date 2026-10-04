from app.rag.code_analyzer import CodeAnalyzer
from app.rag.code_graph import CodeGraph
from app.rag.vector_store import VectorStore


analyzer = CodeAnalyzer()
graph = CodeGraph()
vector_store = VectorStore()

print("Building Code Graph...\n")

# Get all indexed chunks
data = vector_store.collection.get(
    include=["documents", "metadatas"]
)

documents = data["documents"]
metadatas = data["metadatas"]


# Group chunks by file
files = {}

for document, metadata in zip(documents, metadatas):
    file_path = metadata["file"]

    if file_path not in files:
        files[file_path] = []

    files[file_path].append({
        "document": document,
        "start_line": metadata["start_line"],
    })


# Analyze every complete file
for file_path, chunks in files.items():

    # Sort chunks by line number
    chunks.sort(key=lambda x: x["start_line"])

    # Reconstruct complete file
    code = "\n".join(
        chunk["document"]
        for chunk in chunks
    )

    analysis = analyzer.analyze_file(
        file_path,
        code
    )

    graph.add_file(
        file_path,
        analysis
    )


# Build relationships
graph.build_call_edges()


print("GRAPH SUMMARY")
print("=" * 50)

summary = graph.summary()

print("Files:", summary["nodes"])
print("Edges:", summary["edges"])


print("\nSAMPLE EDGES")
print("=" * 50)

for edge in graph.edges[:30]:
    print(
        f"{edge['source']}"
        f" -> "
        f"{edge['target']}"
        f" | {edge['relation']}"
    )