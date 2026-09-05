from pathlib import Path

import pytest

from ai_rag.domain.chunk import Chunk
from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.document_extension import DocumentExtension
from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument, PreProcessedDocumentMetadata
from ai_rag.ingestion.chunking.rule_providers.extension_chunking_rule_provider import ExtensionChunkingRuleProvider
from ai_rag.ingestion.chunking.strategies.recursive_chunking import HEADING_BODY_SEPARATOR, RecursiveChunkingStrategy

DUMMY_WORDS = tuple(f'word{i:03d}' for i in range(1, 61))
DUMMY_TEXT = ' '.join(DUMMY_WORDS)


def _build_document(text: str, extension: DocumentExtension, heading_path: tuple[str, ...] = ()) -> PreProcessedDocument:
    metadata = PreProcessedDocumentMetadata(
        document_source=f'test.{extension.value}',
        document_type='test',
        document_extension=extension.value,
        document_id='test',
        document_lang='es',
        document_version='1.0',
        document_path=Path('dummy') / f'test.{extension.value}',
    )
    return PreProcessedDocument((DocumentBlock(text, heading_path),), metadata)


def _common_overlap_length(previous_text: str, current_text: str) -> int:
    max_len = min(len(previous_text), len(current_text))
    for length in range(max_len, 0, -1):
        if previous_text[-length:] == current_text[:length]:
            return length
    return 0


@pytest.fixture(scope='module')
def rule_provider() -> ExtensionChunkingRuleProvider:
    return ExtensionChunkingRuleProvider()


@pytest.fixture(
    scope='module',
    params=[
        pytest.param(RecursiveChunkerConfig(200, 50), id='size200-overlap50'),
        pytest.param(RecursiveChunkerConfig(120, 30), id='size120-overlap30'),
        pytest.param(RecursiveChunkerConfig(60, 10), id='size60-overlap10'),
    ],
)
def config(request) -> RecursiveChunkerConfig:
    return request.param


@pytest.fixture(scope='module', params=[DocumentExtension.TXT, DocumentExtension.MARKDOWN])
def extension(request) -> DocumentExtension:
    return request.param


@pytest.fixture(scope='module')
def document(extension: DocumentExtension) -> PreProcessedDocument:
    return _build_document(DUMMY_TEXT, extension)


@pytest.fixture(scope='module')
def chunks(
    config: RecursiveChunkerConfig, rule_provider: ExtensionChunkingRuleProvider, document: PreProcessedDocument
) -> list[Chunk]:
    return RecursiveChunkingStrategy(config, rule_provider).chunk(document)


def test_every_chunk_respects_chunk_size(chunks: list[Chunk], config: RecursiveChunkerConfig):
    for chunk in chunks:
        assert len(chunk.text) <= config.chunk_size


def test_no_chunk_is_empty_or_whitespace(chunks: list[Chunk]):
    for chunk in chunks:
        assert chunk.text.strip()


def test_no_word_is_lost(chunks: list[Chunk]):
    seen: list[str] = []
    for chunk in chunks:
        words = chunk.text.split()
        overlap_len = 0
        for candidate_len in range(min(len(seen), len(words)), 0, -1):
            if seen[-candidate_len:] == words[:candidate_len]:
                overlap_len = candidate_len
                break
        seen.extend(words[overlap_len:])

    assert seen == list(DUMMY_WORDS)


def test_consecutive_chunks_share_the_configured_overlap(chunks: list[Chunk], config: RecursiveChunkerConfig):
    for previous_chunk, current_chunk in zip(chunks, chunks[1:]):
        overlap_length = _common_overlap_length(previous_chunk.text, current_chunk.text)
        assert 0 < overlap_length <= config.chunk_overlap


def test_chunk_metadata_is_projected_from_the_document(chunks: list[Chunk], document: PreProcessedDocument):
    for i, chunk in enumerate(chunks, start=1):
        assert chunk.id == f'{document.metadata.document_id}-chunk-{i}'
        assert chunk.document_id == document.metadata.document_id
        assert chunk.index == i
        assert chunk.metadata.source == document.metadata.document_source
        assert chunk.metadata.document_type == document.metadata.document_type
        assert chunk.metadata.lang == document.metadata.document_lang
        assert chunk.metadata.version == document.metadata.document_version
        assert chunk.metadata.path == document.metadata.document_path
        assert chunk.metadata.extension == document.metadata.document_extension


def test_an_unbreakable_token_still_respects_chunk_size(rule_provider: ExtensionChunkingRuleProvider):
    document = _build_document('a' * 500, DocumentExtension.TXT)

    chunks = RecursiveChunkingStrategy(RecursiveChunkerConfig(120, 30), rule_provider).chunk(document)

    assert chunks
    for chunk in chunks:
        assert len(chunk.text) <= 120


def test_chunking_produces_the_expected_chunk_texts(rule_provider: ExtensionChunkingRuleProvider):
    document = _build_document('aa bb cc dd ee ff gg hh', DocumentExtension.TXT)

    chunks = RecursiveChunkingStrategy(RecursiveChunkerConfig(8, 3), rule_provider).chunk(document)

    assert [chunk.text for chunk in chunks] == [
        'aa bb',
        'bb cc',
        'cc dd',
        'dd ee',
        'ee ff',
        'ff gg hh',
    ]


def test_rejects_wrong_config_type(rule_provider: ExtensionChunkingRuleProvider):
    strategy = RecursiveChunkingStrategy(RecursiveChunkerConfig(10, 2), rule_provider)

    with pytest.raises(TypeError):
        strategy.set_config(SentenceChunkerConfig(4, 2))


def test_markdown_chunks_are_prefixed_with_the_heading_breadcrumb(rule_provider: ExtensionChunkingRuleProvider):
    document = _build_document(DUMMY_TEXT, DocumentExtension.MARKDOWN, heading_path=('Vacaciones', 'Solicitud'))

    chunks = RecursiveChunkingStrategy(RecursiveChunkerConfig(60, 10), rule_provider).chunk(document)

    assert chunks
    for chunk in chunks:
        assert chunk.text.startswith('Vacaciones > Solicitud\n\n')
        assert len(chunk.text) <= 60


def test_txt_chunks_from_a_block_without_heading_path_carry_no_prefix(rule_provider: ExtensionChunkingRuleProvider):
    document = _build_document(DUMMY_TEXT, DocumentExtension.TXT)

    chunks = RecursiveChunkingStrategy(RecursiveChunkerConfig(60, 10), rule_provider).chunk(document)

    assert chunks
    assert chunks[0].text.startswith(DUMMY_WORDS[0])
    for chunk in chunks:
        assert HEADING_BODY_SEPARATOR not in chunk.text


def test_oversized_heading_prefix_degrades_to_no_prefix(rule_provider: ExtensionChunkingRuleProvider):
    # 'Vacaciones > Solicitud\n\n' por sí solo ya mide 24 caracteres.
    document = _build_document(DUMMY_TEXT, DocumentExtension.MARKDOWN, heading_path=('Vacaciones', 'Solicitud'))

    chunks = RecursiveChunkingStrategy(RecursiveChunkerConfig(10, 2), rule_provider).chunk(document)

    assert chunks
    for chunk in chunks:
        assert not chunk.text.startswith('Vacaciones')
        assert len(chunk.text) <= 10
