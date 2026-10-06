import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    backend_root = Path(__file__).resolve().parent.parent
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

from app.rag.retriever import Retriever


def main():

    retriever = Retriever()

    results = retriever.retrieve(
        "How are battle questions selected?",
        top_k=1
    )

    if not results:
        print("No results found.")
        return

    result = results[0]
    metadata = result["metadata"]

    print("\n" + "=" * 70)
    print("CODE TRACING")
    print("=" * 70)

    print(
        f"\nStarting file: "
        f"{metadata['file']}"
    )
    print(
        f"Lines: "
        f"{metadata['start_line']}-"
        f"{metadata['end_line']}"
    )

    related = retriever.code_tracer.trace(
        result
    )

    print("\nRELATED CODE:")
    print("-" * 70)

    seen = set()

    for item in related:
        key = (
            item["symbol"],
            item["file"],
            item["start_line"]
        )

        if key in seen:
            continue

        seen.add(key)
        print(
            f"{item['symbol']} → "
            f"{item['file']} "
            f"(Lines "
            f"{item['start_line']}-"
            f"{item['end_line']})"
        )


if __name__ == "__main__":
    main()
