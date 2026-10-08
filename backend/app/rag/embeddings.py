import numpy as np
from fastembed import TextEmbedding

ENCODE_BATCH_SIZE = 32
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingModel:

    def __init__(self):

        self.model: TextEmbedding | None = None

        print("Embedding model initialized lazily.")

    def _load_model(self):
        if self.model is None:
            print(f"Loading ONNX embedding model: {MODEL_NAME}")
            self.model = TextEmbedding(MODEL_NAME, threads=1)
            print("ONNX embedding model loaded.")

    def generate_embeddings(self, texts):
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        self._load_model()
        if self.model is None:
            raise RuntimeError("Embedding model failed to initialize.")
        # FastEmbed parallel=0 starts workers on every core; keep inference
        # in-process instead.
        return np.asarray(
            list(
                self.model.embed(
                    texts,
                    batch_size=ENCODE_BATCH_SIZE,
                )
            ),
            dtype=np.float32,
        )

    def generate_query_embedding(self, query):
        self._load_model()
        if self.model is None:
            raise RuntimeError("Embedding model failed to initialize.")
        return next(
            iter(
                self.model.query_embed(
                    query,
                )
            )
        )