import unittest
from unittest.mock import Mock, patch

from app.rag import retriever as retriever_module
from app.rag.retriever import Retriever


class EmptyCorpusRetrieverTests(unittest.TestCase):
    def test_tokenize_replaces_existing_punctuation_in_one_pass(self):
        self.assertEqual(
            Retriever.tokenize('Foo(bar){baz}[qux];,.:/\\ "it\'s"'),
            ["foo", "bar", "baz", "qux", "it", "s"],
        )

    def test_empty_collection_initializes_and_returns_no_keyword_results(self):
        vector_store = Mock()
        vector_store.collection.get.return_value = {
            "documents": [],
            "metadatas": [],
        }

        with (
            patch.object(retriever_module, "EmbeddingModel"),
            patch.object(
                retriever_module,
                "VectorStore",
                return_value=vector_store,
            ),
            patch.object(retriever_module, "Reranker"),
        ):
            retriever = Retriever()

        self.assertEqual(retriever.keyword_search("anything"), [])

    def test_nonempty_collection_keeps_keyword_search_working(self):
        vector_store = Mock()
        vector_store.collection.get.return_value = {
            "documents": ["alpha function", "beta class"],
            "metadatas": [
                {"file": "alpha.py", "start_line": 1, "end_line": 1},
                {"file": "beta.py", "start_line": 1, "end_line": 1},
            ],
        }

        with (
            patch.object(retriever_module, "EmbeddingModel"),
            patch.object(
                retriever_module,
                "VectorStore",
                return_value=vector_store,
            ),
            patch.object(retriever_module, "Reranker"),
        ):
            retriever = Retriever()

        results = retriever.keyword_search("alpha")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["document"], "alpha function")

    def test_keyword_search_returns_stable_top_k_without_sorting_every_hit(self):
        retriever = Retriever.__new__(Retriever)
        retriever.documents = ["first", "second", "third", "fourth"]
        retriever.metadatas = [{"file": name} for name in retriever.documents]
        retriever.bm25 = Mock()
        retriever.bm25.get_scores.return_value = [1.0, 3.0, 3.0, 2.0]

        results = retriever.keyword_search("query", top_k=2)

        self.assertEqual(
            [result["document"] for result in results],
            ["second", "third"],
        )
        self.assertEqual(
            [result["bm25_score"] for result in results],
            [3.0, 3.0],
        )

        negative_limit_results = retriever.keyword_search(
            "query",
            top_k=-1,
        )
        self.assertEqual(
            [result["document"] for result in negative_limit_results],
            ["second", "third", "fourth"],
        )


if __name__ == "__main__":
    unittest.main()
