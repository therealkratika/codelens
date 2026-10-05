from app.evaluation_dataset import EVALUATION_DATASET
from app.rag.retriever import Retriever


def evaluate():
    retriever = Retriever()

    total_precision = 0
    total_recall = 0
    total_mrr = 0

    print("\n" + "=" * 70)
    print("CODELENS RETRIEVAL EVALUATION")
    print("=" * 70)

    for item in EVALUATION_DATASET:

        question = item["question"]
        expected_files = set(item["expected_files"])

        print(f"\nQuestion: {question}")

        results = retriever.retrieve(
            question,
            top_k=5,
            prefer_code=True
        )

        retrieved_files = [
            result["metadata"]["file"]
            for result in results
        ]

        print("Retrieved:")
        for rank, file_path in enumerate(retrieved_files, start=1):
            print(f"  {rank}. {file_path}")

        # -------------------------
        # Precision@5
        # -------------------------

        unique_retrieved_files = set(retrieved_files)

        relevant_count = sum(
           1 for file_path in unique_retrieved_files
           if file_path in expected_files
        )

        precision = relevant_count / len(retrieved_files) if retrieved_files else 0

        # -------------------------
        # Recall@5
        # -------------------------

        recall = relevant_count / len(expected_files) if expected_files else 0

        # -------------------------
        # MRR
        # -------------------------

        reciprocal_rank = 0

        for rank, file_path in enumerate(retrieved_files, start=1):
            if file_path in expected_files:
                reciprocal_rank = 1 / rank
                break

        total_precision += precision
        total_recall += recall
        total_mrr += reciprocal_rank

        print(f"Precision@5: {precision:.2f}")
        print(f"Recall@5:    {recall:.2f}")
        print(f"MRR:         {reciprocal_rank:.2f}")

    # -------------------------
    # Average scores
    # -------------------------

    count = len(EVALUATION_DATASET)

    avg_precision = total_precision / count
    avg_recall = total_recall / count
    avg_mrr = total_mrr / count

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    print(f"Average Precision@5: {avg_precision:.2f}")
    print(f"Average Recall@5:    {avg_recall:.2f}")
    print(f"Average MRR:         {avg_mrr:.2f}")

    print("=" * 70)


if __name__ == "__main__":
    evaluate()