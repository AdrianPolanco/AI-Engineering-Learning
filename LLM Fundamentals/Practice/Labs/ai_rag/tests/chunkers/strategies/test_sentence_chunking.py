from pathlib import Path

import pytest

from ai_rag.domain.chunk_config import SentenceChunkerConfig
from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument, PreProcessedDocumentMetadata
from ai_rag.ingestion.chunking.strategies.sentence_chunking import SentenceChunkingStrategy


@pytest.fixture()
def DUMMY_TEXT() -> str:
    return """
            The user sends an HTTP request.
            The API validates the request.
            The application authenticates the user.
            The service retrieves the account.
            The database returns the account data.
            The service processes the account data.
            The API builds the response.
            The server sends the response to the client.
            The client receives the response.
            The operation is completed successfully.
            """

def _sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in text.split('.') if sentence.strip()]

@pytest.fixture(params=[(4,2), (5,3), (3,1)])
def sentence_chunker(request) -> SentenceChunkingStrategy:
    max_sentences, overlap = request.param
    config = SentenceChunkerConfig(max_sentences, overlap)
    return SentenceChunkingStrategy(config)

def test_sentence_chunking_with_single_block(DUMMY_TEXT: str, sentence_chunker: SentenceChunkingStrategy):
    block = DocumentBlock(DUMMY_TEXT)
    metadata = PreProcessedDocumentMetadata('test.txt', 'test', 'txt', 'test', 'es', '1.0', Path('C:/dummy/test.txt'))
    processed_doc = PreProcessedDocument((block,), metadata)
    chunks = sentence_chunker.chunk(processed_doc)

    current_config = sentence_chunker.get_config()

    assert chunks

    for i, chunk in enumerate(chunks):
        sentences = _sentences(chunk.text)

        assert len(sentences) <= current_config.max_sentences

        if i > 0:
            prev_chunk = chunks[i - 1]
            prev_chunk_sentences = _sentences(prev_chunk.text)
            overlapped_sentences = prev_chunk_sentences[-current_config.overlap_sentences:]
            initial_overlapped_sentences = sentences[:current_config.overlap_sentences]

            assert overlapped_sentences == initial_overlapped_sentences

@pytest.mark.parametrize('max_sentences, overlap', [(1, 2), (2, 2), (0, 0), (3, -1)])
def test_sentence_chunker_config_rejects_invalid_overlap(max_sentences: int, overlap: int):
    with pytest.raises(ValueError):
        SentenceChunkerConfig(max_sentences, overlap)
