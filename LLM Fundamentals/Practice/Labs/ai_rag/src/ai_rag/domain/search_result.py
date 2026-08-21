from dataclasses import dataclass
from ai_rag.domain.chunk import Chunk


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float