from app.rag.rag_pipeline import RAGPipeline


def main():

    repository_root = "./repositories/Nextja_coding_battle"

    rag = RAGPipeline(
        repository_root
    )

    question = input(
        "\nAsk CodeLens: "
    )

    answer_started = False

    def display_answer_text(text):
        nonlocal answer_started

        if not answer_started:
            print("\n")
            print("=" * 70)
            print("CODELENS")
            print("=" * 70)
            print("\nANSWER")
            print("-" * 70)
            answer_started = True

        print(text, end="", flush=True)

    result = rag.answer(
        question,
        on_text=display_answer_text
    )

    if not answer_started:
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
            f"{source['file']} "
            f"(Lines {source['start_line']}-"
            f"{source['end_line']})"
        )


if __name__ == "__main__":
    main()