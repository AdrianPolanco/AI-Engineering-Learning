from collections.abc import Iterator

import numpy as np

from ai_rag.domain.chunk import Chunk
from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SemanticChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument
from ai_rag.embeddings.sentence_embedder import SentenceEmbedder
from ai_rag.ingestion.chunking.chunking_strategy import UNSUPPORTED_CONFIG_MESSAGE, ChunkingStrategy
from ai_rag.ingestion.chunking.text_windowing import build_heading_prefix, merge_windows, seed_overlap, split_fragments

SENTENCE_SEPARATOR = '.'
SENTENCE_TRAILING_SPACE = ' '
WORD_SEPARATORS = (' ', '')


class SemanticChunkingStrategy(ChunkingStrategy):
    def __init__(self, config: SemanticChunkerConfig, embedder: SentenceEmbedder) -> None:
        super().__init__()
        self.set_config(config)
        self.__embedder = embedder

    def chunk(self, document: PreProcessedDocument) -> list[Chunk]:
        metadata = self._build_chunk_metadata(document.metadata)
        document_id = document.metadata.document_id

        return [
            Chunk(
                id=f'{document_id}-chunk-{index}',
                document_id=document_id,
                index=index,
                text=body,
                metadata=metadata,
            )
            for index, body in enumerate(self.__iter_chunk_bodies(document), start=1)
        ]

    def __iter_chunk_bodies(self, document: PreProcessedDocument) -> Iterator[str]:
        for block in document.text:
            yield from self.__chunk_bodies_for_block(block)

    def __chunk_bodies_for_block(self, block: DocumentBlock) -> Iterator[str]:
        prefix = build_heading_prefix(block.heading_path)
        budget = self.__config.max_chunk_size - len(prefix)
        if budget < 1:
            # El heading no cabe junto con contenido útil: se degrada sin prefijo antes que abortar.
            prefix = ''
            budget = self.__config.max_chunk_size
        effective_overlap = min(self.__config.overlap_size, budget - 1)

        stripped_sentences = self.__split_sentences(block.text)
        if not stripped_sentences:
            return
        fragments = self.__attach_separators(stripped_sentences)

        raw_groups = self.__detect_raw_groups(stripped_sentences, fragments)
        topics = self.__merge_tiny_topics(raw_groups)

        previous_last_window: list[str] | None = None
        for topic_index, topic in enumerate(topics):
            windows = self.__windows_for_topic(topic, budget, effective_overlap)
            for window_index, window in enumerate(windows):
                # El puente de overlap solo cruza fronteras entre temas: dentro de un mismo tema
                # partido por tamaño, merge_windows ya sembró el overlap internamente.
                if topic_index > 0 and window_index == 0 and previous_last_window is not None:
                    window = seed_overlap(previous_last_window, effective_overlap) + window
                body = ''.join(window).strip()
                if body:
                    yield f'{prefix}{body}'
            if windows:
                previous_last_window = windows[-1]

    def __windows_for_topic(self, topic: list[str], budget: int, effective_overlap: int) -> list[list[str]]:
        topic_length = sum(len(fragment) for fragment in topic)
        if topic_length <= budget:
            # El tema entero cabe en el tope: una única ventana, sin invocar merge_windows/split_fragments.
            return [list(topic)]

        expanded: list[str] = []
        for fragment in topic:
            if len(fragment) > budget:
                expanded.extend(split_fragments(fragment, WORD_SEPARATORS, budget))
            else:
                expanded.append(fragment)
        return merge_windows(expanded, budget, effective_overlap)

    def __detect_raw_groups(self, stripped_sentences: list[str], fragments: list[str]) -> list[list[str]]:
        if len(stripped_sentences) <= 1:
            return [list(fragments)] if fragments else []

        embeddings = self.__embedder.embed_many(stripped_sentences)
        distances = [
            1 - self.__embedder.similarity(embeddings[i], embeddings[i + 1])
            for i in range(len(stripped_sentences) - 1)
        ]
        threshold = float(np.percentile(distances, self.__config.breakpoint_percentile_threshold))

        groups: list[list[str]] = [[fragments[0]]]
        for i in range(1, len(fragments)):
            if distances[i - 1] > threshold:
                groups.append([fragments[i]])
            else:
                groups[-1].append(fragments[i])
        return groups

    def __merge_tiny_topics(self, raw_groups: list[list[str]]) -> list[list[str]]:
        min_chunk_size = self.__config.min_chunk_size
        total_groups = len(raw_groups)
        topics: list[list[str]] = []
        index = 0

        while index < total_groups:
            current = list(raw_groups[index])
            current_length = sum(len(fragment) for fragment in current)
            index += 1
            while current_length < min_chunk_size and index < total_groups:
                current.extend(raw_groups[index])
                current_length += sum(len(fragment) for fragment in raw_groups[index])
                index += 1
            topics.append(current)

        # Excepción: fusión hacia atrás solo para el último tema del bloque, si aún es diminuto.
        if len(topics) > 1 and sum(len(fragment) for fragment in topics[-1]) < min_chunk_size:
            last_topic = topics.pop()
            topics[-1].extend(last_topic)

        return topics

    @staticmethod
    def __split_sentences(text: str) -> list[str]:
        return [stripped for sentence in text.split(SENTENCE_SEPARATOR) if (stripped := sentence.strip())]

    @staticmethod
    def __attach_separators(stripped_sentences: list[str]) -> list[str]:
        last_index = len(stripped_sentences) - 1
        return [
            f'{sentence}{SENTENCE_SEPARATOR}'
            if i == last_index
            else f'{sentence}{SENTENCE_SEPARATOR}{SENTENCE_TRAILING_SPACE}'
            for i, sentence in enumerate(stripped_sentences)
        ]

    def set_config(self, config: RecursiveChunkerConfig | SemanticChunkerConfig | SentenceChunkerConfig) -> None:
        if not isinstance(config, SemanticChunkerConfig):
            raise TypeError(UNSUPPORTED_CONFIG_MESSAGE.format(config_type=SemanticChunkerConfig.__name__))
        self.__config = config

    def get_config(self) -> SemanticChunkerConfig:
        return self.__config
