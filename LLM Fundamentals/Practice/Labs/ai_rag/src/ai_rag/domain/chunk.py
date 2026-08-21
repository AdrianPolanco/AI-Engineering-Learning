from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ChunkMetadata:
    source: str
    document_type: str
    language: str

@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    text: str
    index: int
    metadata: ChunkMetadata