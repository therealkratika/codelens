from rank_bm25 import BM25Okapi

from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore
from app.rag.reranker import Reranker


class Retriever:

    def __init__(self):

        print("Initializing retriever...")

        # --------------------------------
        # Embedding model
        # --------------------------------

        self.embedding_model = EmbeddingModel()

        # --------------------------------
        # Vector store
        # --------------------------------

        self.vector_store = VectorStore()

        # --------------------------------
        # Reranker
        # --------------------------------

        self.reranker = Reranker()

        # --------------------------------
        # Load all indexed chunks
        # --------------------------------

        data = self.vector_store.collection.get(
            include=[
                "documents",
                "metadatas"
            ]
        )

        self.documents = data["documents"]
        self.metadatas = data["metadatas"]

        # --------------------------------
        # Prepare BM25 keyword index
        # --------------------------------

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

    # =================================================
    # TOKENIZATION
    # =================================================

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
            .replace(":", " ")
            .replace("/", " ")
            .replace("\\", " ")
            .replace('"', " ")
            .replace("'", " ")
            .split()
        )

    # =================================================
    # SEMANTIC SEARCH
    # =================================================

    def semantic_search(
        self,
        query,
        top_k=20
    ):

        # Generate query embedding
        query_embedding = (
            self.embedding_model
            .generate_query_embedding(query)
        )

        # Search ChromaDB
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

    # =================================================
    # KEYWORD SEARCH - BM25
    # =================================================

    def keyword_search(
        self,
        query,
        top_k=20
    ):

        # Tokenize query
        query_tokens = self.tokenize(
            query
        )

        # Calculate BM25 scores
        scores = self.bm25.get_scores(
            query_tokens
        )

        # Sort document indices
        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        results = []

        for index in ranked_indices[:top_k]:

            results.append({

                "document":
                    self.documents[index],

                "metadata":
                    self.metadatas[index],

                "bm25_score":
                    float(scores[index])

            })

        return results

    # =================================================
    # HYBRID RETRIEVAL
    # =================================================

    def hybrid_search(
        self,
        query,
        candidate_k=20
    ):

        # --------------------------------
        # Semantic search
        # --------------------------------

        semantic_results = (
            self.semantic_search(
                query,
                top_k=candidate_k
            )
        )

        # --------------------------------
        # Keyword search
        # --------------------------------

        keyword_results = (
            self.keyword_search(
                query,
                top_k=candidate_k
            )
        )

        # --------------------------------
        # Reciprocal Rank Fusion
        # --------------------------------

        scores = {}

        result_data = {}

        # --------------------------------
        # Semantic ranking weight = 0.6
        # --------------------------------

        for rank, result in enumerate(
            semantic_results,
            start=1
        ):

            metadata = result["metadata"]

            key = (
                metadata["file"],
                metadata["start_line"],
                metadata["end_line"]
            )

            scores[key] = (
                scores.get(key, 0)
                +
                0.6 / (60 + rank)
            )

            result_data[key] = result

        # --------------------------------
        # Keyword ranking weight = 0.4
        # --------------------------------

        for rank, result in enumerate(
            keyword_results,
            start=1
        ):

            metadata = result["metadata"]

            key = (
                metadata["file"],
                metadata["start_line"],
                metadata["end_line"]
            )

            scores[key] = (
                scores.get(key, 0)
                +
                0.4 / (60 + rank)
            )

            result_data[key] = result

        # --------------------------------
        # Sort hybrid results
        # --------------------------------

        ranked_keys = sorted(
            scores.keys(),
            key=lambda key: scores[key],
            reverse=True
        )

        candidates = []

        for key in ranked_keys[:candidate_k]:

            result = result_data[key]

            candidates.append({

                "document":
                    result["document"],

                "metadata":
                    result["metadata"],

                "hybrid_score":
                    scores[key]

            })

        return candidates

    # =================================================
    # FINAL RETRIEVAL + RERANKING
    # =================================================

    def retrieve(
        self,
        query,
        top_k=5
    ):

        print(
            "\nRunning hybrid retrieval..."
        )

        # --------------------------------
        # Get 20 candidates
        # --------------------------------

        candidates = self.hybrid_search(
            query,
            candidate_k=20
        )

        print(
            f"Hybrid retrieval found "
            f"{len(candidates)} candidates."
        )

        # --------------------------------
        # Rerank candidates
        # --------------------------------

        print(
            "Reranking candidates..."
        )

        final_results = (
            self.reranker.rerank(
                query,
                candidates,
                top_k=top_k
            )
        )

        print(
            f"Returning top "
            f"{len(final_results)} results."
        )

        return final_results