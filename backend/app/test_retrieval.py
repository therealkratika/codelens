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
    print("RETRIEVED RESULTS")
    print("=" * 70)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i in range(len(documents)):

        metadata = metadatas[i]

        print("\n" + "-" * 70)

        print(f"Result #{i + 1}")

        print(
            f"File: {metadata['file']}"
        )

        print(
            f"Lines: "
            f"{metadata['start_line']}-"
            f"{metadata['end_line']}"
        )

        print(
            f"Distance: {distances[i]:.4f}"
        )

        print("\nCode:")

        print(
            documents[i][:1000]
        )


if __name__ == "__main__":
    main()