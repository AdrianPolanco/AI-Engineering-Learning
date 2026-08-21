from dataclasses import dataclass

@dataclass(frozen=True)
class ChunkPayload:
    chunk_id: str
    document_id: str
    source: str
    score: float

@dataclass(frozen=True)
class RAGResponse:
    answer: str
    sources: list[ChunkPayload]