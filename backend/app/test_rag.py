from app.rag.rag_pipeline import RAGPipeline


def main():

    rag = RAGPipeline()

    question = input(
        "\nAsk CodeLens: "
    )

    answer = rag.answer(
        question
    )

    print("\n")
    print("=" * 70)
    print("CODELENS")
    print("=" * 70)

    print(answer)


if __name__ == "__main__":
    main()