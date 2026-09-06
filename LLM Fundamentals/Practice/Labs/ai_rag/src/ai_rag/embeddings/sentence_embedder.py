from typing import Protocol

import numpy as np


class SentenceEmbedder(Protocol):
    def embed_many(self, texts: list[str]) -> np.ndarray: ...
    def similarity(self, a: np.ndarray, b: np.ndarray) -> float: ...
