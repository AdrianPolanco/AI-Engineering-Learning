from dataclasses import dataclass

@dataclass(frozen=True)
class SentenceChunkerConfig:
    max_sentences: int
    overlap_sentences: int

@dataclass(frozen=True)
class RecursiveChunkerConfig:
    chunk_size: int
    chunk_overlap: int