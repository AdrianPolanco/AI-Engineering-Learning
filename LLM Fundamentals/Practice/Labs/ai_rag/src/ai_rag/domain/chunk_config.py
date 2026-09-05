from dataclasses import dataclass

MIN_MAX_SENTENCES_MESSAGE = 'max_sentences must be at least 1'
MIN_OVERLAP_SENTENCES_MESSAGE = 'overlap_sentences must not be negative'
OVERLAP_NOT_LESS_THAN_MAX_MESSAGE = 'overlap_sentences must be less than max_sentences'

@dataclass(frozen=True)
class SentenceChunkerConfig:
    max_sentences: int
    overlap_sentences: int

    def __post_init__(self) -> None:
        if self.max_sentences < 1:
            raise ValueError(MIN_MAX_SENTENCES_MESSAGE)
        if self.overlap_sentences < 0:
            raise ValueError(MIN_OVERLAP_SENTENCES_MESSAGE)
        if self.overlap_sentences >= self.max_sentences:
            raise ValueError(OVERLAP_NOT_LESS_THAN_MAX_MESSAGE)

MIN_CHUNK_SIZE_MESSAGE = 'chunk_size must be at least 1'
MIN_CHUNK_OVERLAP_MESSAGE = 'chunk_overlap must not be negative'
OVERLAP_NOT_LESS_THAN_SIZE_MESSAGE = 'chunk_overlap must be less than chunk_size'

@dataclass(frozen=True)
class RecursiveChunkerConfig:
    chunk_size: int
    chunk_overlap: int

    def __post_init__(self) -> None:
        if self.chunk_size < 1:
            raise ValueError(MIN_CHUNK_SIZE_MESSAGE)
        if self.chunk_overlap < 0:
            raise ValueError(MIN_CHUNK_OVERLAP_MESSAGE)
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(OVERLAP_NOT_LESS_THAN_SIZE_MESSAGE)
