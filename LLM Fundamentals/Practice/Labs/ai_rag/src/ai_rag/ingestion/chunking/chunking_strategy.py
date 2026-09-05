from abc import ABC, abstractmethod

from ai_rag.domain.chunk import Chunk, ChunkMetadata
from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.pre_processed_document import PreProcessedDocument, PreProcessedDocumentMetadata

UNSUPPORTED_CONFIG_MESSAGE = 'This chunking strategy only accepts configs of type {config_type}'

class ChunkingStrategy(ABC):

    @abstractmethod
    def chunk(self, document: PreProcessedDocument) -> list[Chunk]:
        pass

    @abstractmethod
    def set_config(self, config: RecursiveChunkerConfig|SentenceChunkerConfig):
        pass

    @staticmethod
    def _build_chunk_metadata(metadata: PreProcessedDocumentMetadata) -> ChunkMetadata:
        return ChunkMetadata(
            source=metadata.document_source,
            document_type=metadata.document_type,
            lang=metadata.document_lang,
            version=metadata.document_version,
            path=metadata.document_path,
            extension=metadata.document_extension,
        )
