from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):

        print("Loading reranker model...")

        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

        print("Reranker model loaded!")

    def rerank(
        self,
        query,
        candidates,
        top_k=5
    ):

        if not candidates:
            return []

        # --------------------------------
        # Create query-document pairs
        # --------------------------------

        pairs = []

        for candidate in candidates:

            document = candidate["document"]

            pairs.append([
                query,
                document
            ])

        # --------------------------------
        # Calculate relevance scores
        # --------------------------------

        scores = self.model.predict(
            pairs
        )

        # --------------------------------
        # Attach reranking score
        # --------------------------------

        ranked_candidates = []

        for candidate, score in zip(
            candidates,
            scores
        ):

            ranked_candidates.append({
                **candidate,
                "rerank_score": float(score)
            })

        # --------------------------------
        # Sort by reranker score
        # --------------------------------

        ranked_candidates.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return ranked_candidates[:top_k]