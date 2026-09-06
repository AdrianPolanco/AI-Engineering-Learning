import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model: str):
        self.model_name = model
        self.embedding_model =  SentenceTransformer(self.model_name)

    def embed(self, text: str) -> np.ndarray:
        return self.embedding_model.encode(text, convert_to_numpy=True)

    def embed_many(self, texts: list[str]) -> np.ndarray:
        return self.embedding_model.encode(texts, convert_to_numpy=True)

    def get_model_info(self) -> dict[str, int|str|None]:
        return {
            'model_name': self.model_name,
            'dimensions': self.embedding_model.get_sentence_embedding_dimension()
        }

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))