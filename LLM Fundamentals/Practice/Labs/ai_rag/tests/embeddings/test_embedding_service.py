import numpy as np
import pytest

from ai_rag.embeddings.embedding_service import EmbeddingService


class FakeSentenceTransformer:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def encode(self, texts, convert_to_numpy: bool = True):
        if isinstance(texts, str):
            return np.array([1.0, 0.0, 0.0])
        return np.array([[1.0, 0.0, 0.0] for _ in texts])

    def get_sentence_embedding_dimension(self) -> int:
        return 3


@pytest.fixture
def embedding_service(monkeypatch: pytest.MonkeyPatch) -> EmbeddingService:
    monkeypatch.setattr(
        'ai_rag.embeddings.embedding_service.SentenceTransformer',
        FakeSentenceTransformer,
    )
    return EmbeddingService('fake-model')


def test_get_model_info_does_not_raise_and_returns_the_fake_dimension(embedding_service: EmbeddingService):
    info = embedding_service.get_model_info()

    assert info['model_name'] == 'fake-model'
    assert info['dimensions'] == 3


def test_similarity_returns_one_for_identical_vectors(embedding_service: EmbeddingService):
    vector = np.array([1.0, 2.0, 3.0])

    assert embedding_service.similarity(vector, vector) == pytest.approx(1.0)
