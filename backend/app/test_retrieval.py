from abc import ABC, abstractmethod

from app.rag.retriever import Retriever


class ResultPrinter(ABC):
    @abstractmethod
    def print_result_header(self):
        """Print the heading shown before retrieval results."""

    @abstractmethod
    def print_result(self, index, result):
        """Format a single retrieval result for display."""

    @abstractmethod
    def print_summary(self, results):
        """Render the complete retrieval results list."""


class ConsoleResultPrinter(ResultPrinter):
    def print_result_header(self):
        print("\n" + "=" * 70)
        print("HYBRID + RERANKED RETRIEVAL RESULTS")
        print("=" * 70)

    def print_result(self, index, result):
        metadata = result["metadata"]

        print("\n" + "-" * 70)
        print(f"Result #{index}")
        print(f"File: {metadata['file']}")
        print(
            f"Lines: "
            f"{metadata['start_line']}-"
            f"{metadata['end_line']}"
        )
        print(f"Hybrid Score: {result['hybrid_score']:.6f}")
        print(f"Rerank Score: {result['rerank_score']:.6f}")
        print(f"Code Boost: {result['code_boost']:.2f}")
        print(f"Final Score: {result['final_score']:.6f}")

    def print_summary(self, results):
        self.print_result_header()
        for i, result in enumerate(results, start=1):
            self.print_result(i, result)


def main():

    retriever = Retriever()
    printer = ConsoleResultPrinter()

    query = input(
        "\nAsk something about the codebase: "
    )

    results = retriever.retrieve(
        query,
        top_k=5
    )

    printer.print_summary(results)


if __name__ == "__main__":
    main()