import heapq
import os

from rank_bm25 import BM25Okapi

from app.rag.code_tracer import CodeTracer
from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore
from app.rag.reranker import Reranker


class Retriever:

    _TOKEN_TRANSLATION = str.maketrans({
        character: " "
        for character in "(){}[];,.:/\\\"'"
    })

    def __init__(self, repository_path=None):

        print("Initializing retriever...")
        # Embedding model
        self.embedding_model = EmbeddingModel()
        # Vector store

        self.vector_store = VectorStore(
            repository_path
        )
        # Reranker
        self.enable_reranker = (
            os.getenv(
                "CODELENS_ENABLE_RERANKER",
                "true"
            ).lower()
            == "true"
        )

        if self.enable_reranker:

            print("Reranker enabled.")

            self.reranker = Reranker()

        else:

            print(
                "Reranker disabled "
                "(CODELENS_ENABLE_RERANKER=false)."
            )

            self.reranker = None

        # --------------------------------
        # Load indexed chunks
        # --------------------------------

        data = self.vector_store.collection.get(
            include=[
                "documents",
                "metadatas"
            ]
        )

        self.documents = data["documents"]
        self.metadatas = data["metadatas"]

        self.code_tracer = CodeTracer(
            self.documents,
            self.metadatas
        )

        # --------------------------------
        # Prepare BM25 keyword index
        # --------------------------------

        tokenized_documents = [
            self.tokenize(document)
            for document in self.documents
        ]

        self.bm25 = (
            BM25Okapi(tokenized_documents)
            if tokenized_documents
            else None
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

        return text.lower().translate(
            Retriever._TOKEN_TRANSLATION
        ).split()

    # =================================================
    # SEMANTIC SEARCH
    # =================================================

    def semantic_search(
        self,
        query,
        top_k=20
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

    # =================================================
    # KEYWORD SEARCH - BM25
    # =================================================

    def keyword_search(
        self,
        query,
        top_k=20
    ):

        if self.bm25 is None:

            return []

        query_tokens = self.tokenize(
            query
        )

        scores = self.bm25.get_scores(
            query_tokens
        )

        result_count = (
            top_k
            if top_k >= 0
            else max(len(scores) + top_k, 0)
        )
        ranked_indices = heapq.nlargest(
            result_count,
            range(len(scores)),
            key=scores.__getitem__
        )

        results = []

        for index in ranked_indices:

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
        # Semantic weight = 0.6
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
        # Keyword weight = 0.4
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

    # FINAL RETRIEVAL

    def retrieve(
        self,
        query,
        top_k=5,
        prefer_code=False
    ):

        print(
            "\nRunning hybrid retrieval..."
        )

        # --------------------------------
        # 1. Hybrid candidates
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
        # 2. Optional reranking
        # --------------------------------

        if self.enable_reranker:

            print(
                "Reranking candidates..."
            )

            ranked_results = (
                self.reranker.rerank(
                    query,
                    candidates,
                    top_k=20
                )
            )

        else:

            print(
                "Skipping reranking."
            )

            ranked_results = []

            for candidate in candidates:

                candidate["rerank_score"] = (
                    candidate["hybrid_score"]
                )

                ranked_results.append(
                    candidate
                )

            ranked_results.sort(
                key=lambda x: x["rerank_score"],
                reverse=True
            )
        # 3. Code-aware ranking
        code_extensions = {

            "js",
            "jsx",
            "ts",
            "tsx",
            "py",
            "java",
            "cpp",
            "c",
            "h",
            "hpp",
            "go",
            "rs"

        }

        documentation_files = {

            "readme.md",
            "integration_guide.md",
            "contributing.md",
            "changelog.md"

        }

        for result in ranked_results:

            code_boost = 0.0

            documentation_penalty = 0.0

            if prefer_code:

                file_path = (
                    result["metadata"]["file"]
                )

                extension = (
                    file_path
                    .rsplit(".", 1)[-1]
                    .lower()
                )

                file_name = (
                    file_path
                    .rsplit("/", 1)[-1]
                    .lower()
                )

                if extension in code_extensions:

                    code_boost = 1.0

                if file_name in documentation_files:

                    documentation_penalty = 0.5

            result["code_boost"] = (
                code_boost
            )

            result["documentation_penalty"] = (
                documentation_penalty
            )

            result["final_score"] = (
                result["rerank_score"]
                + code_boost
                - documentation_penalty
            )
        # 4. Sort by final score
        ranked_results.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )
        # 5. One result per file
        unique_results = []

        seen_files = set()

        for result in ranked_results:

            file_path = (
                result["metadata"]["file"]
            )

            if file_path in seen_files:

                continue

            seen_files.add(file_path)

            unique_results.append(
                result
            )

            if len(unique_results) == top_k:

                break

        print(
            f"Returning top "
            f"{len(unique_results)} results."
        )

        return unique_results