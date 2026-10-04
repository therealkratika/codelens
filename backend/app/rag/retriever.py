from rank_bm25 import BM25Okapi

from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore


class Retriever:

    def __init__(self):

        print("Initializing retriever...")

        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()

        # Load all indexed chunks for keyword search
        data = self.vector_store.collection.get(
            include=["documents", "metadatas"]
        )

        self.documents = data["documents"]
        self.metadatas = data["metadatas"]

        # Prepare BM25 corpus
        tokenized_documents = [
            self.tokenize(document)
            for document in self.documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

        print(
            f"Keyword index loaded: "
            f"{len(self.documents)} chunks"
        )

    # ------------------------------------------------
    # Tokenization
    # ------------------------------------------------

    @staticmethod
    def tokenize(text):

        return (
            text.lower()
            .replace("(", " ")
            .replace(")", " ")
            .replace("{", " ")
            .replace("}", " ")
            .replace("[", " ")
            .replace("]", " ")
            .replace(";", " ")
            .replace(",", " ")
            .replace(".", " ")
            .split()
        )

    # ------------------------------------------------
    # Semantic retrieval
    # ------------------------------------------------

    def semantic_search(
        self,
        query,
        top_k=10
    ):

        query_embedding = (
            self.embedding_model
            .generate_query_embedding(query)
        )

        results = self.vector_store.search(
            query_embedding,
            top_k
        )

        semantic_results = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(documents)):

            semantic_results.append({
                "document": documents[i],
                "metadata": metadatas[i],
                "distance": distances[i]
            })

        return semantic_results

    # Keyword retrieval

    def keyword_search(
        self,
        query,
        top_k=10
    ):

        query_tokens = self.tokenize(query)

        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        results = []

        for index in ranked_indices[:top_k]:

            results.append({
                "document": self.documents[index],
                "metadata": self.metadatas[index],
                "bm25_score": float(scores[index])
            })

        return results

    # ------------------------------------------------
    # Hybrid retrieval
    # ------------------------------------------------

    def retrieve(
        self,
        query,
        top_k=5
    ):

        semantic_results = self.semantic_search(
            query,
            top_k=10
        )

        keyword_results = self.keyword_search(
            query,
            top_k=10
        )

        # --------------------------------------------
        # Combine using Reciprocal Rank Fusion
        # --------------------------------------------

        scores = {}
        result_data = {}

        # Semantic ranking
        for rank, result in enumerate(
            semantic_results,
            start=1
        ):

            key = (
                result["metadata"]["file"],
                result["metadata"]["start_line"],
                result["metadata"]["end_line"]
            )

            scores[key] = scores.get(key, 0) + (
                0.6 / (60 + rank)
            )

            result_data[key] = result

        # Keyword ranking
        for rank, result in enumerate(
            keyword_results,
            start=1
        ):

            key = (
                result["metadata"]["file"],
                result["metadata"]["start_line"],
                result["metadata"]["end_line"]
            )

            scores[key] = scores.get(key, 0) + (
                0.4 / (60 + rank)
            )

            result_data[key] = result
        # Sort combined results
        ranked_keys = sorted(
            scores.keys(),
            key=lambda key: scores[key],
            reverse=True
        )

        final_results = []

        for key in ranked_keys[:top_k]:

            result = result_data[key]

            final_results.append({
                "document": result["document"],
                "metadata": result["metadata"],
                "hybrid_score": scores[key]
            })

        return final_results