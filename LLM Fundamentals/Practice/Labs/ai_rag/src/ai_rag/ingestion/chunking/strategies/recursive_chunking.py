from collections.abc import Iterator

from ai_rag.domain.chunk import Chunk
from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.document_extension import DocumentExtension
from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument
from ai_rag.ingestion.chunking.chunking_rule_provider import ChunkingRuleProvider
from ai_rag.ingestion.chunking.chunking_strategy import UNSUPPORTED_CONFIG_MESSAGE, ChunkingStrategy
from ai_rag.ingestion.chunking.text_windowing import build_heading_prefix, merge_windows, split_fragments


class RecursiveChunkingStrategy(ChunkingStrategy):
    def __init__(self, config: RecursiveChunkerConfig, rule_provider: ChunkingRuleProvider) -> None:
        super().__init__()
        self.set_config(config)
        self.__rule_provider = rule_provider

    def chunk(self, document: PreProcessedDocument) -> list[Chunk]:
        metadata = self._build_chunk_metadata(document.metadata)
        document_id = document.metadata.document_id
        extension = DocumentExtension(document.metadata.document_extension)
        separators = self.__rule_provider.get_rules(extension).separators

        return [
            Chunk(
                id=f'{document_id}-chunk-{index}',
                document_id=document_id,
                index=index,
                text=body,
                metadata=metadata,
            )
            for index, body in enumerate(self.__iter_chunk_bodies(document, separators), start=1)
        ]

    def __iter_chunk_bodies(self, document: PreProcessedDocument, separators: tuple[str, ...]) -> Iterator[str]:
        for block in document.text:
            yield from self.__chunk_bodies_for_block(block, separators)

    def __chunk_bodies_for_block(self, block: DocumentBlock, separators: tuple[str, ...]) -> Iterator[str]:
        prefix = build_heading_prefix(block.heading_path)
        budget = self.__config.chunk_size - len(prefix)
        if budget < 1:
            # El heading no cabe junto con contenido útil: se degrada sin prefijo antes que abortar.
            prefix = ''
            budget = self.__config.chunk_size
        effective_overlap = min(self.__config.chunk_overlap, budget - 1)

        fragments = split_fragments(block.text, separators, budget)
        for window in merge_windows(fragments, budget, effective_overlap):
            body = ''.join(window).strip()
            if body:
                yield f'{prefix}{body}'

    def set_config(self, config: RecursiveChunkerConfig | SentenceChunkerConfig) -> None:
        if not isinstance(config, RecursiveChunkerConfig):
            raise TypeError(UNSUPPORTED_CONFIG_MESSAGE.format(config_type=RecursiveChunkerConfig.__name__))
        self.__config = config

    def get_config(self) -> RecursiveChunkerConfig:
        return self.__config
