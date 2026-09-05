from ai_rag.domain.chunk import Chunk
from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.pre_processed_document import PreProcessedDocument
from ai_rag.ingestion.chunking.chunking_strategy import ChunkingStrategy


class RecursiveChunkingStrategy(ChunkingStrategy):
    def __init__(self, config: RecursiveChunkerConfig) -> None:
        super().__init__()

    def chunk(self, document: PreProcessedDocument) -> list[Chunk]:
        return super().chunk(document)

    def set_config(self, config: RecursiveChunkerConfig | SentenceChunkerConfig):
        if type(config) is not RecursiveChunkerConfig:
            raise NotImplementedError(f'This chunking strategy only accepts configs of type {RecursiveChunkerConfig.__name__}')
        super().set_config(config)