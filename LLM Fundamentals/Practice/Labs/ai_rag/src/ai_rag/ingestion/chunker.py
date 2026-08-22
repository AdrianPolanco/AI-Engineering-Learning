from ai_rag.domain.chunk import Chunk
from ai_rag.domain.document import Document
from ai_rag.ingestion.chunking.chunking_strategy import ChunkingStrategy
from ai_rag.ingestion.pre_processor import DocumentPreProcessor


class Chunker:
    def __init__(self, preprocessor: DocumentPreProcessor, strategy: ChunkingStrategy) -> None:
        self.__preprocessor = preprocessor
        self.__strategy = strategy

    def chunk(self, document: Document) -> list[Chunk]:
        processed_doc = self.__preprocessor.process(document)

        return self.__strategy.chunk(processed_doc)