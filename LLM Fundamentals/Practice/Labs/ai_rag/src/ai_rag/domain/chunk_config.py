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

MIN_MAX_CHUNK_SIZE_MESSAGE = 'max_chunk_size must be at least 1'
MIN_MIN_CHUNK_SIZE_MESSAGE = 'min_chunk_size must be at least 1'
MIN_CHUNK_SIZE_NOT_LESS_THAN_MAX_MESSAGE = 'min_chunk_size must be less than max_chunk_size'
MIN_OVERLAP_SIZE_MESSAGE = 'overlap_size must not be negative'
SEMANTIC_OVERLAP_NOT_LESS_THAN_MAX_MESSAGE = 'overlap_size must be less than max_chunk_size'
INVALID_BREAKPOINT_PERCENTILE_MESSAGE = 'breakpoint_percentile_threshold must be between 0 and 100'

@dataclass(frozen=True)
class SemanticChunkerConfig:
    max_chunk_size: int
    min_chunk_size: int
    overlap_size: int
    breakpoint_percentile_threshold: float = 95.0

    def __post_init__(self) -> None:
        if self.max_chunk_size < 1:
            raise ValueError(MIN_MAX_CHUNK_SIZE_MESSAGE)
        if self.min_chunk_size < 1:
            raise ValueError(MIN_MIN_CHUNK_SIZE_MESSAGE)
        if self.min_chunk_size >= self.max_chunk_size:
            raise ValueError(MIN_CHUNK_SIZE_NOT_LESS_THAN_MAX_MESSAGE)
        if self.overlap_size < 0:
            raise ValueError(MIN_OVERLAP_SIZE_MESSAGE)
        if self.overlap_size >= self.max_chunk_size:
            raise ValueError(SEMANTIC_OVERLAP_NOT_LESS_THAN_MAX_MESSAGE)
        if not 0 <= self.breakpoint_percentile_threshold <= 100:
            raise ValueError(INVALID_BREAKPOINT_PERCENTILE_MESSAGE)
