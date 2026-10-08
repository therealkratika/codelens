from sentence_transformers import SentenceTransformer

ENCODE_BATCH_SIZE = 8


class EmbeddingModel:

    def __init__(self):

        self.model = None

        print("Embedding model initialized lazily.")

    def _load_model(self):

        if self.model is None:

            print("Loading embedding model...")

            self.model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

            print("Embedding model loaded!")

    def generate_embeddings(self, texts):

        if not texts:
            return []

        self._load_model()

        return self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=ENCODE_BATCH_SIZE,
            convert_to_numpy=True
        )

    def generate_query_embedding(self, query):

        self._load_model()

        return self.model.encode(
            [query],
            convert_to_numpy=True
        )[0]