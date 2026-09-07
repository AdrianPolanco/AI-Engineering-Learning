from pathlib import Path

import numpy as np
import pytest

from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SemanticChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument, PreProcessedDocumentMetadata
from ai_rag.ingestion.chunking.strategies.semantic_chunking import SemanticChunkingStrategy


class UniformFakeEmbedder:
    """Mismo vector para toda frase: la distancia coseno es siempre 0, nunca hay frontera."""

    def embed_many(self, texts: list[str]) -> np.ndarray:
        return np.array([[1.0, 0.0] for _ in texts])

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class LookupFakeEmbedder:
    """Vector fijo por texto de frase exacto, para forzar fronteras semánticas específicas."""

    def __init__(self, vectors: dict[str, tuple[float, ...]]) -> None:
        self.__vectors = vectors

    def embed_many(self, texts: list[str]) -> np.ndarray:
        return np.array([self.__vectors[text] for text in texts])

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _build_document(text: str, heading_path: tuple[str, ...] = ()) -> PreProcessedDocument:
    metadata = PreProcessedDocumentMetadata(
        document_source='test.md',
        document_type='test',
        document_extension='md',
        document_id='test',
        document_lang='es',
        document_version='1.0',
        document_path=Path('dummy') / 'test.md',
    )
    return PreProcessedDocument((DocumentBlock(text, heading_path),), metadata)


def _common_overlap_length(previous_text: str, current_text: str) -> int:
    max_len = min(len(previous_text), len(current_text))
    for length in range(max_len, 0, -1):
        if previous_text[-length:] == current_text[:length]:
            return length
    return 0


# ---------------------------------------------------------------------------
# Dos clusters: la frontera semántica delimita el chunk, sin ventanear por tamaño.
# ---------------------------------------------------------------------------

CLUSTER_A_SENTENCES = (
    'Los sistemas distribuidos replican su estado',
    'Cada nodo mantiene un log local',
    'La consistencia eventual simplifica el diseño',
)
CLUSTER_B_SENTENCES = (
    'El equipo comercial gestiona los contratos',
    'Los precios varían según el volumen',
    'Cada cliente recibe una factura mensual',
)


def _two_cluster_embedder() -> LookupFakeEmbedder:
    vectors: dict[str, tuple[float, ...]] = {}
    vectors.update({sentence: (1.0, 0.0) for sentence in CLUSTER_A_SENTENCES})
    vectors.update({sentence: (0.0, 1.0) for sentence in CLUSTER_B_SENTENCES})
    return LookupFakeEmbedder(vectors)


def test_two_clusters_produce_exactly_two_chunks_one_per_cluster():
    last_fragment_of_cluster_a = f'{CLUSTER_A_SENTENCES[-1]}. '
    config = SemanticChunkerConfig(
        max_chunk_size=1000, min_chunk_size=10, overlap_size=len(last_fragment_of_cluster_a)
    )
    text = '. '.join(CLUSTER_A_SENTENCES + CLUSTER_B_SENTENCES) + '.'
    document = _build_document(text)

    chunks = SemanticChunkingStrategy(config, _two_cluster_embedder()).chunk(document)

    assert len(chunks) == 2
    for sentence in CLUSTER_A_SENTENCES:
        assert sentence in chunks[0].text
    for sentence in CLUSTER_B_SENTENCES:
        assert sentence not in chunks[0].text
        assert sentence in chunks[1].text
    # El overlap bridging antepone la última frase del cluster A al segundo chunk.
    assert chunks[1].text.startswith(CLUSTER_A_SENTENCES[-1])


def test_two_clusters_below_min_chunk_size_merge_into_a_single_chunk():
    config = SemanticChunkerConfig(max_chunk_size=20_000, min_chunk_size=10_000, overlap_size=5)
    text = '. '.join(CLUSTER_A_SENTENCES + CLUSTER_B_SENTENCES) + '.'
    document = _build_document(text)

    chunks = SemanticChunkingStrategy(config, _two_cluster_embedder()).chunk(document)

    assert len(chunks) == 1
    for sentence in CLUSTER_A_SENTENCES + CLUSTER_B_SENTENCES:
        assert sentence in chunks[0].text


# ---------------------------------------------------------------------------
# Tres grupos: el último, diminuto, se funde hacia atrás en vez de forward.
# ---------------------------------------------------------------------------

GROUP_A_SENTENCES = tuple(f'frase a{i:02d}' for i in range(1, 11))  # grupo grande, ya >= min_chunk_size
GROUP_B_SENTENCES = tuple(f'frase b{i:02d}' for i in range(1, 11))  # grupo grande, ya >= min_chunk_size
GROUP_C_SENTENCES = tuple(f'frase c{i:02d}' for i in range(1, 4))  # grupo diminuto, al final del bloque


def _three_group_embedder() -> LookupFakeEmbedder:
    vectors: dict[str, tuple[float, ...]] = {}
    vectors.update({sentence: (1.0, 0.0, 0.0) for sentence in GROUP_A_SENTENCES})
    vectors.update({sentence: (0.0, 1.0, 0.0) for sentence in GROUP_B_SENTENCES})
    vectors.update({sentence: (0.0, 0.0, 1.0) for sentence in GROUP_C_SENTENCES})
    return LookupFakeEmbedder(vectors)


def test_tiny_final_raw_group_merges_backward_into_the_previous_topic():
    config = SemanticChunkerConfig(max_chunk_size=2000, min_chunk_size=50, overlap_size=5)
    text = '. '.join(GROUP_A_SENTENCES + GROUP_B_SENTENCES + GROUP_C_SENTENCES) + '.'
    document = _build_document(text)

    chunks = SemanticChunkingStrategy(config, _three_group_embedder()).chunk(document)

    assert len(chunks) == 2
    for sentence in GROUP_A_SENTENCES:
        assert sentence in chunks[0].text
    for sentence in GROUP_B_SENTENCES:
        assert sentence not in chunks[0].text
        assert sentence in chunks[1].text
    for sentence in GROUP_C_SENTENCES:
        # El grupo diminuto se fusiona con el tema anterior (B), no queda como chunk propio.
        assert sentence in chunks[1].text


# ---------------------------------------------------------------------------
# Un único tema (sin fronteras), sujeto a las mismas reglas que RecursiveChunkingStrategy
# cuando desborda max_chunk_size.
# ---------------------------------------------------------------------------

DUMMY_SENTENCES = tuple(f'palabra{i:03d}' for i in range(1, 31))
DUMMY_TEXT = '. '.join(DUMMY_SENTENCES) + '.'


def test_oversized_topic_splits_into_bounded_chunks_with_overlap():
    # overlap_size debe cubrir al menos una frase completa ('palabraNNN. ' ~ 12 caracteres):
    # merge_windows opera a granularidad de frase aquí, no de palabra como en RecursiveChunkingStrategy.
    config = SemanticChunkerConfig(max_chunk_size=60, min_chunk_size=5, overlap_size=15)
    document = _build_document(DUMMY_TEXT)

    chunks = SemanticChunkingStrategy(config, UniformFakeEmbedder()).chunk(document)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.text) <= 60
    for previous_chunk, current_chunk in zip(chunks, chunks[1:]):
        overlap_length = _common_overlap_length(previous_chunk.text, current_chunk.text)
        assert 0 < overlap_length <= config.overlap_size


def test_no_sentence_is_lost_or_reordered():
    config = SemanticChunkerConfig(max_chunk_size=60, min_chunk_size=5, overlap_size=10)
    document = _build_document(DUMMY_TEXT)

    chunks = SemanticChunkingStrategy(config, UniformFakeEmbedder()).chunk(document)

    seen: list[str] = []
    for chunk in chunks:
        tokens = chunk.text.split()
        overlap_len = 0
        for candidate_len in range(min(len(seen), len(tokens)), 0, -1):
            if seen[-candidate_len:] == tokens[:candidate_len]:
                overlap_len = candidate_len
                break
        seen.extend(tokens[overlap_len:])

    assert seen == [f'{sentence}.' for sentence in DUMMY_SENTENCES]


def test_no_chunk_is_empty_or_whitespace_only():
    config = SemanticChunkerConfig(max_chunk_size=60, min_chunk_size=5, overlap_size=10)
    document = _build_document(DUMMY_TEXT)

    chunks = SemanticChunkingStrategy(config, UniformFakeEmbedder()).chunk(document)

    assert chunks
    for chunk in chunks:
        assert chunk.text.strip()


def test_an_unbreakable_sentence_still_respects_max_chunk_size():
    document = _build_document('a' * 500 + '.')
    config = SemanticChunkerConfig(max_chunk_size=120, min_chunk_size=5, overlap_size=30)

    chunks = SemanticChunkingStrategy(config, UniformFakeEmbedder()).chunk(document)

    assert chunks
    for chunk in chunks:
        assert len(chunk.text) <= 120


def test_markdown_chunks_are_prefixed_with_the_heading_breadcrumb():
    config = SemanticChunkerConfig(max_chunk_size=60, min_chunk_size=5, overlap_size=10)
    document = _build_document(DUMMY_TEXT, heading_path=('Vacaciones', 'Solicitud'))

    chunks = SemanticChunkingStrategy(config, UniformFakeEmbedder()).chunk(document)

    assert chunks
    for chunk in chunks:
        assert chunk.text.startswith('Vacaciones > Solicitud\n\n')
        assert len(chunk.text) <= 60


def test_oversized_heading_prefix_degrades_to_no_prefix():
    # 'Vacaciones > Solicitud\n\n' por sí solo ya mide 24 caracteres.
    config = SemanticChunkerConfig(max_chunk_size=10, min_chunk_size=2, overlap_size=2)
    document = _build_document(DUMMY_TEXT, heading_path=('Vacaciones', 'Solicitud'))

    chunks = SemanticChunkingStrategy(config, UniformFakeEmbedder()).chunk(document)

    assert chunks
    for chunk in chunks:
        assert not chunk.text.startswith('Vacaciones')
        assert len(chunk.text) <= 10


def test_rejects_wrong_config_type():
    config = SemanticChunkerConfig(max_chunk_size=100, min_chunk_size=10, overlap_size=5)
    strategy = SemanticChunkingStrategy(config, UniformFakeEmbedder())

    with pytest.raises(TypeError):
        strategy.set_config(RecursiveChunkerConfig(10, 2))
    with pytest.raises(TypeError):
        strategy.set_config(SentenceChunkerConfig(4, 2))
