from collections.abc import Iterator

from ai_rag.domain.chunk import Chunk, ChunkMetadata
from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.pre_processed_document import PreProcessedDocument, PreProcessedDocumentMetadata
from ai_rag.ingestion.chunking.chunking_strategy import ChunkingStrategy

SENTENCE_SEPARATOR = '.'
SENTENCE_JOINER = ' '
UNSUPPORTED_CONFIG_MESSAGE = 'This chunking strategy only accepts configs of type {config_type}'


class SentenceChunkingStrategy(ChunkingStrategy):
    def __init__(self, config: SentenceChunkerConfig) -> None:
        super().__init__()
        self.set_config(config)

    def chunk(self, document: PreProcessedDocument) -> list[Chunk]:
        # La metadata del chunk es idéntica para todo el documento, por tanto se proyecta una sola vez.
        metadata = self.__build_chunk_metadata(document.metadata)
        document_id = document.metadata.document_id

        return [
            Chunk(
                id=f'{document_id}-chunk-{index}',
                document_id=document_id,
                index=index,
                text=SENTENCE_JOINER.join(window),
                metadata=metadata,
            )
            for index, window in enumerate(self.__iter_windows(document), start=1)
        ]

    def __iter_windows(self, document: PreProcessedDocument) -> Iterator[list[str]]:
        for block in document.text:
            yield from self.__sliding_windows(self.__split_sentences(block.text))

    def __sliding_windows(self, sentences: list[str]) -> Iterator[list[str]]:
        max_sentences = self.__config.max_sentences # 5
        step = max_sentences - self.__config.overlap_sentences  # >= 1 garantizado por el config # 5 - 2 = 3

        start = 0
        total = len(sentences) # 12
        while start < total: #1. 0 < 12 = False 2. 3 < 12 3. 6 < 12 4. 9 < 12
            end = start + max_sentences #1. 0 + 5 2. 3 + 5 3. 6 + 5 4. 9 + 5
            yield sentences[start:end] #1. 0:5 2. 3:8 3. 6:11 4. 9:14
            # Se corta al alcanzar el final: evita una última ventana ya contenida en la anterior.
            if end >= total: #1. 5 >= 12 2. 8 >= 12 3. 11 >= 12 4. 14 >= 12
                return
            start += step #1. 0 + 3 2. 3 + 3 3. 6 + 3

    @staticmethod
    def __split_sentences(text: str) -> list[str]:
        return [
            f'{stripped}{SENTENCE_SEPARATOR}'
            for sentence in text.split(SENTENCE_SEPARATOR)
            if (stripped := sentence.strip())
        ]

    @staticmethod
    def __build_chunk_metadata(metadata: PreProcessedDocumentMetadata) -> ChunkMetadata:
        return ChunkMetadata(
            source=metadata.document_source,
            document_type=metadata.document_type,
            lang=metadata.document_lang,
            version=metadata.document_version,
            path=metadata.document_path,
            extension=metadata.document_extension,
        )

    def set_config(self, config: RecursiveChunkerConfig | SentenceChunkerConfig) -> None:
        if not isinstance(config, SentenceChunkerConfig):
            raise TypeError(UNSUPPORTED_CONFIG_MESSAGE.format(config_type=SentenceChunkerConfig.__name__))
        self.__config = config

    def get_config(self) -> SentenceChunkerConfig:
        return self.__config


# ==========================================================================
# VERSIÓN ANTERIOR — conservada solo para comparar con el refactor.
# ==========================================================================
# from ai_rag.domain.chunk import Chunk, ChunkMetadata
# from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig
# from ai_rag.domain.pre_processed_document import PreProcessedDocument
# from ai_rag.ingestion.chunking.chunking_strategy import ChunkingStrategy
#
#
# class SentenceChunkingStrategy(ChunkingStrategy):
#     def __init__(self, config: SentenceChunkerConfig) -> None:
#         super().__init__()
#         self.__config = config
#
#     def chunk(self, document: PreProcessedDocument) -> list[Chunk]:
#         chunks: list[Chunk] = []
#         chunk_n = 1
#         # [DocumentBlock, DocumentBlock]
#         for block in document.text:
#             # DocumentBlock.text
#             sentences = [
#                 f'{sentence.strip()}.'
#                 for sentence in block.text.split('.')
#                 if sentence.strip()
#             ]
#
#             buffer = []
#             #overlap_pointer = 0
#             overlap_added = False
#             for i, sentence in enumerate(sentences):
#
#                 if not overlap_added and i > 0 and len(buffer) == 0:
#                     overlap_sentences = sentences[max(0, i - self.__config.overlap_sentences):i]
#                     buffer.extend(overlap_sentences)
#                     overlap_added = True
#
#                 if len(buffer) < self.__config.max_sentences:
#                     buffer.append(sentence)
#
#                 if len(buffer) == self.__config.max_sentences or i == len(sentences) - 1:
#                     overlap_added, chunk_n = self.__create_chunk(document, chunks, chunk_n, buffer)
#
#         return chunks
#
#     def __create_chunk(self, document, chunks, chunk_n, buffer):
#         chunk_id = f'{document.metadata.document_id}-chunk-{chunk_n}'
#
#         chunk_metadata = ChunkMetadata(
#                     source=document.metadata.document_source,
#                     document_type= document.metadata.document_type,
#                     lang=document.metadata.document_lang,
#                     version=document.metadata.document_version,
#                     path=document.metadata.document_path,
#                     extension=document.metadata.document_extension
#                 )
#
#         chunks.append(Chunk(
#                     id=chunk_id,
#                     document_id=document.metadata.document_id,
#                     index=chunk_n,
#                     text=' '.join(buffer), metadata=chunk_metadata))
#
#         buffer.clear()
#         chunk_n += 1
#         overlap_added = False
#         return overlap_added, chunk_n
#
#     def set_config(self, config: RecursiveChunkerConfig | SentenceChunkerConfig):
#         if type(config) is not SentenceChunkerConfig:
#             raise NotImplementedError(f'This chunking strategy only accepts configs of type {SentenceChunkerConfig.__name__}')
#         self.__config = config
#
#     def get_config(self) -> SentenceChunkerConfig:
#         return self.__config
