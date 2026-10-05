from app.evaluation_dataset import EVALUATION_DATASET
from app.rag.rag_pipeline import RAGPipeline


REPOSITORY_ROOT = "./repositories/Nextja_coding_battle"


def evaluate():
    rag = RAGPipeline(REPOSITORY_ROOT)

    print("\n" + "=" * 70)
    print("CODELENS PIPELINE EVALUATION")
    print("=" * 70)

    for item in EVALUATION_DATASET:
        question = item["question"]
        expected_files = set(item["expected_files"])

        print(f"\nQuestion: {question}")

        # Run the actual CodeLens pipeline
        answer = rag.answer(question)

        print("\nAnswer:")
        print(answer)

        print("\nExpected files:")
        for file_path in expected_files:
            print(f"  - {file_path}")

    print("\n" + "=" * 70)
    print("PIPELINE EVALUATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    evaluate()