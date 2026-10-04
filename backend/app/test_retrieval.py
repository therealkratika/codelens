from app.rag.retriever import Retriever


def main():

    retriever = Retriever()

    query = input(
        "\nAsk something about the codebase: "
    )

    results = retriever.retrieve(
        query,
        top_k=5
    )

    print("\n" + "=" * 70)
    print("HYBRID RETRIEVAL RESULTS")
    print("=" * 70)

    for i, result in enumerate(
        results,
        start=1
    ):

        metadata = result["metadata"]

        print("\n" + "-" * 70)

        print(f"Result #{i}")

        print(
            f"File: {metadata['file']}"
        )

        print(
            f"Lines: "
            f"{metadata['start_line']}-"
            f"{metadata['end_line']}"
        )

        print(
            f"Hybrid Score: "
            f"{result['hybrid_score']:.6f}"
        )

        print("\nCode:")

        print(
            result["document"][:1000]
        )


if __name__ == "__main__":
    main()