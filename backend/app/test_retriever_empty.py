import unittest
from unittest.mock import Mock, patch

from app.rag import retriever as retriever_module
from app.rag.retriever import Retriever


class EmptyCorpusRetrieverTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
