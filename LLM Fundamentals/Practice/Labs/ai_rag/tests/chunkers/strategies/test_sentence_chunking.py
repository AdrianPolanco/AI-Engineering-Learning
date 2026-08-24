from pathlib import Path

import pytest

from ai_rag.domain.chunk import Chunk
from ai_rag.domain.chunk_config import SentenceChunkerConfig
from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument, PreProcessedDocumentMetadata
from ai_rag.ingestion.chunking.strategies.sentence_chunking import SentenceChunkingStrategy

DUMMY_SENTENCES = (
    'The user sends an HTTP request',
    'The API validates the request',
    'The application authenticates the user',
    'The service retrieves the account',
    'The database returns the account data',
    'The service processes the account data',
    'The API builds the response',
    'The server sends the response to the client',
    'The client receives the response',
    'The operation is completed successfully',
)
DUMMY_TEXT = '\n'.join(f'{sentence}.' for sentence in DUMMY_SENTENCES)


def _build_document(text: str) -> PreProcessedDocument:
    metadata = PreProcessedDocumentMetadata(
        document_source='test.txt',
        document_type='test',
        document_extension='txt',
        document_id='test',
        document_lang='es',
        document_version='1.0',
        document_path=Path('dummy') / 'test.txt',
    )
    return PreProcessedDocument((DocumentBlock(text),), metadata)


def _sentences(text: str) -> list[str]:
    # Re-implementación deliberada del split de la estrategia (no se importa el helper de
    # producción): si el test llamara al mismo código que construye los chunks, un bug en el
    # split no lo detectaría nadie.
    return [sentence.strip() for sentence in text.split('.') if sentence.strip()]


@pytest.fixture(scope='module')
def processed_document() -> PreProcessedDocument:
    return _build_document(DUMMY_TEXT)


@pytest.fixture(
    scope='module',
    params=[
        pytest.param(SentenceChunkerConfig(4, 2), id='max4-overlap2'),
        pytest.param(SentenceChunkerConfig(5, 3), id='max5-overlap3'),
        pytest.param(SentenceChunkerConfig(3, 1), id='max3-overlap1'),
    ],
)
def config(request) -> SentenceChunkerConfig:
    return request.param


@pytest.fixture(scope='module')
def chunks(config: SentenceChunkerConfig, processed_document: PreProcessedDocument) -> list[Chunk]:
    return SentenceChunkingStrategy(config).chunk(processed_document)


def test_every_chunk_respects_max_sentences(chunks: list[Chunk], config: SentenceChunkerConfig):
    for chunk in chunks:
        assert len(_sentences(chunk.text)) <= config.max_sentences


def test_consecutive_chunks_share_the_configured_overlap(chunks: list[Chunk], config: SentenceChunkerConfig):
    for previous_chunk, current_chunk in zip(chunks, chunks[1:]):
        previous_sentences = _sentences(previous_chunk.text)
        current_sentences = _sentences(current_chunk.text)

        overlapped_sentences = previous_sentences[-config.overlap_sentences:]
        leading_sentences = current_sentences[:config.overlap_sentences]

        assert overlapped_sentences == leading_sentences


def test_no_sentence_is_lost(chunks: list[Chunk]):
    seen: list[str] = []
    for chunk in chunks:
        for sentence in _sentences(chunk.text):
            if sentence not in seen:
                seen.append(sentence)

    assert seen == list(DUMMY_SENTENCES)


def test_chunk_metadata_is_projected_from_the_document(chunks: list[Chunk], processed_document: PreProcessedDocument):
    for i, chunk in enumerate(chunks, start=1):
        assert chunk.id == f'{processed_document.metadata.document_id}-chunk-{i}'
        assert chunk.document_id == processed_document.metadata.document_id
        assert chunk.index == i
        assert chunk.metadata.source == processed_document.metadata.document_source
        assert chunk.metadata.document_type == processed_document.metadata.document_type
        assert chunk.metadata.lang == processed_document.metadata.document_lang
        assert chunk.metadata.version == processed_document.metadata.document_version
        assert chunk.metadata.path == processed_document.metadata.document_path
        assert chunk.metadata.extension == processed_document.metadata.document_extension


def test_chunking_produces_the_expected_chunk_texts():
    document = _build_document('One. Two. Three. Four. Five.')

    chunks = SentenceChunkingStrategy(SentenceChunkerConfig(3, 1)).chunk(document)

    assert [chunk.text for chunk in chunks] == ['One. Two. Three.', 'Three. Four. Five.']


# ==========================================================================
# VERSIÓN ANTERIOR — conservada solo para comparar con el refactor.
# Eliminar este bloque una vez validada la nueva versión.
# ==========================================================================
# from pathlib import Path
#
# import pytest
#
# from ai_rag.domain.chunk_config import SentenceChunkerConfig
# from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument, PreProcessedDocumentMetadata
# from ai_rag.ingestion.chunking.strategies.sentence_chunking import SentenceChunkingStrategy
#
#
# @pytest.fixture()
# def DUMMY_TEXT() -> str:
#     return """
#             The user sends an HTTP request.
#             The API validates the request.
#             The application authenticates the user.
#             The service retrieves the account.
#             The database returns the account data.
#             The service processes the account data.
#             The API builds the response.
#             The server sends the response to the client.
#             The client receives the response.
#             The operation is completed successfully.
#             """
#
# def _sentences(text: str) -> list[str]:
#     return [sentence.strip() for sentence in text.split('.') if sentence.strip()]
#
# @pytest.fixture(params=[(4,2), (5,3), (3,1)])
# def sentence_chunker(request) -> SentenceChunkingStrategy:
#     max_sentences, overlap = request.param
#     config = SentenceChunkerConfig(max_sentences, overlap)
#     return SentenceChunkingStrategy(config)
#
# def test_sentence_chunking_with_single_block(DUMMY_TEXT: str, sentence_chunker: SentenceChunkingStrategy):
#     block = DocumentBlock(DUMMY_TEXT)
#     metadata = PreProcessedDocumentMetadata('test.txt', 'test', 'txt', 'test', 'es', '1.0', Path('C:/dummy/test.txt'))
#     processed_doc = PreProcessedDocument((block,), metadata)
#     chunks = sentence_chunker.chunk(processed_doc)
#
#     current_config = sentence_chunker.get_config()
#
#     assert chunks
#
#     for i, chunk in enumerate(chunks):
#         sentences = _sentences(chunk.text)
#
#         assert len(sentences) <= current_config.max_sentences
#
#         if i > 0:
#             prev_chunk = chunks[i - 1]
#             prev_chunk_sentences = _sentences(prev_chunk.text)
#             overlapped_sentences = prev_chunk_sentences[-current_config.overlap_sentences:]
#             initial_overlapped_sentences = sentences[:current_config.overlap_sentences]
#
#             assert overlapped_sentences == initial_overlapped_sentences
#
# @pytest.mark.parametrize('max_sentences, overlap', [(1, 2), (2, 2), (0, 0), (3, -1)])
# def test_sentence_chunker_config_rejects_invalid_overlap(max_sentences: int, overlap: int):
#     with pytest.raises(ValueError):
#         SentenceChunkerConfig(max_sentences, overlap)
