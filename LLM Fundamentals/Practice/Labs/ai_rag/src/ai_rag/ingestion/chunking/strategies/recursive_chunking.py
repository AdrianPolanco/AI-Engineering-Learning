from collections.abc import Iterator

from ai_rag.domain.chunk import Chunk
from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.document_extension import DocumentExtension
from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument
from ai_rag.ingestion.chunking.chunking_rule_provider import ChunkingRuleProvider
from ai_rag.ingestion.chunking.chunking_strategy import UNSUPPORTED_CONFIG_MESSAGE, ChunkingStrategy

HEADING_JOINER = ' > '
HEADING_BODY_SEPARATOR = '\n\n'


def _build_prefix(heading_path: tuple[str, ...]) -> str:
    if not heading_path:
        return ''
    return f'{HEADING_JOINER.join(heading_path)}{HEADING_BODY_SEPARATOR}'


def _split_fragments(text: str, separators: tuple[str, ...], budget: int) -> list[str]:
    # Content-preserving: ''.join(_split_fragments(text, separators, budget)) == text.
    if not text:
        return []
    if len(text) <= budget:
        return [text]
    if not separators:
        # Se agotó la lista de separadores sin llegar a '': último recurso, trocear a tamaño fijo.
        return [text[i : i + budget] for i in range(0, len(text), budget)]

    separator, *remaining = separators
    pieces = list(text) if separator == '' else _split_keeping_separator(text, separator)

    fragments: list[str] = []
    for piece in pieces:
        if len(piece) <= budget:
            fragments.append(piece)
        else:
            fragments.extend(_split_fragments(piece, remaining, budget))
    return fragments


def _split_keeping_separator(text: str, separator: str) -> list[str]:
    # El separador se conserva pegado al final de cada trozo (salvo el último), de modo que
    # ''.join(...) reconstruye el texto exactamente.
    parts = text.split(separator)
    pieces = [f'{part}{separator}' for part in parts[:-1]]
    pieces.append(parts[-1])
    return pieces


def _merge_windows(fragments: list[str], budget: int, effective_overlap: int) -> list[list[str]]:
    windows: list[list[str]] = []
    current: list[str] = []
    current_len = 0

    for fragment in fragments:
        fragment_len = len(fragment)
        while current and current_len + fragment_len > budget:
            windows.append(current)
            current = _seed_overlap(current, effective_overlap)
            current_len = sum(len(piece) for piece in current)
        current.append(fragment)
        current_len += fragment_len

    if current:
        windows.append(current)
    return windows


def _seed_overlap(window: list[str], effective_overlap: int) -> list[str]:
    if effective_overlap <= 0:
        return []

    suffix: list[str] = []
    suffix_len = 0
    for fragment in reversed(window):
        if suffix_len + len(fragment) > effective_overlap:
            break
        suffix.insert(0, fragment)
        suffix_len += len(fragment)

    # Sufijo propio: garantiza que la siguiente ventana siempre avanza.
    if len(suffix) == len(window):
        suffix = suffix[1:]
    return suffix


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
        prefix = _build_prefix(block.heading_path)
        budget = self.__config.chunk_size - len(prefix)
        if budget < 1:
            # El heading no cabe junto con contenido útil: se degrada sin prefijo antes que abortar.
            prefix = ''
            budget = self.__config.chunk_size
        effective_overlap = min(self.__config.chunk_overlap, budget - 1)

        fragments = _split_fragments(block.text, separators, budget)
        for window in _merge_windows(fragments, budget, effective_overlap):
            body = ''.join(window).strip()
            if body:
                yield f'{prefix}{body}'

    def set_config(self, config: RecursiveChunkerConfig | SentenceChunkerConfig) -> None:
        if not isinstance(config, RecursiveChunkerConfig):
            raise TypeError(UNSUPPORTED_CONFIG_MESSAGE.format(config_type=RecursiveChunkerConfig.__name__))
        self.__config = config

    def get_config(self) -> RecursiveChunkerConfig:
        return self.__config
