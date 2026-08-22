from abc import ABC, abstractmethod

from ai_rag.domain.chunk import Chunk
from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.pre_processed_document import PreProcessedDocument

class ChunkingStrategy(ABC):

    @abstractmethod
    def chunk(self, document: PreProcessedDocument) -> list[Chunk]:
        pass

    @abstractmethod
    def set_config(self, config: RecursiveChunkerConfig|SentenceChunkerConfig):
        pass
