from app.answer_evaluation_dataset import ANSWER_EVALUATION_DATASET
from app.rag.retriever import Retriever


def evaluate():
    retriever = Retriever()

    total_questions = len(ANSWER_EVALUATION_DATASET)
    questions_with_expected_source = 0

    print("\n" + "=" * 70)
    print("CODELENS CITATION / SOURCE EVALUATION")
    print("=" * 70)

    for item in ANSWER_EVALUATION_DATASET:

        question = item["question"]
        expected_sources = set(item["expected_sources"])

        print("\n" + "-" * 70)
        print(f"Question: {question}")
        print("-" * 70)

        results = retriever.retrieve(
            question,
            top_k=5,
            prefer_code=True
        )

        retrieved_sources = []

        for result in results:
            file_path = result["metadata"]["file"]

            if file_path not in retrieved_sources:
                retrieved_sources.append(file_path)

        print("\nRetrieved sources:")

        for rank, file_path in enumerate(
            retrieved_sources,
            start=1
        ):
            print(f"  {rank}. {file_path}")

        matched_sources = [
            file_path
            for file_path in retrieved_sources
            if file_path in expected_sources
        ]

        print("\nExpected sources:")

        for source in expected_sources:
            print(f"  - {source}")

        print("\nMatched sources:")

        if matched_sources:
            for source in matched_sources:
                print(f"  ✅ {source}")

            questions_with_expected_source += 1

        else:
            print("  ❌ No expected source retrieved.")

        source_coverage = (
            len(matched_sources)
            / len(expected_sources)
            if expected_sources
            else 0
        )

        print(
            f"\nSource coverage: "
            f"{source_coverage:.2f}"
        )

    overall_coverage = (
        questions_with_expected_source
        / total_questions
        if total_questions
        else 0
    )

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    print(
        f"Questions with at least one "
        f"expected source: "
        f"{questions_with_expected_source}/"
        f"{total_questions}"
    )

    print(
        f"Question source coverage: "
        f"{overall_coverage:.2%}"
    )

    print("=" * 70)


if __name__ == "__main__":
    evaluate()