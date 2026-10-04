from app.rag.rag_pipeline import RAGPipeline


def main():

    rag = RAGPipeline()

    question = input(
        "\nAsk CodeLens: "
    )

    result = rag.answer(question)

    print("\n")
    print("=" * 70)
    print("CODELENS")
    print("=" * 70)

    print("\nANSWER")
    print("-" * 70)

    print(result["answer"])

    print("\nSOURCES")
    print("-" * 70)

    for source in result["sources"]:

        print(
            f"📄 {source['file']} "
            f"(Lines {source['start_line']}-"
            f"{source['end_line']})"
        )


if __name__ == "__main__":
    main()