import re

import pytest

from ai_rag.domain.chunk_config import (
    MIN_CHUNK_OVERLAP_MESSAGE,
    MIN_CHUNK_SIZE_MESSAGE,
    MIN_MAX_SENTENCES_MESSAGE,
    MIN_OVERLAP_SENTENCES_MESSAGE,
    OVERLAP_NOT_LESS_THAN_MAX_MESSAGE,
    OVERLAP_NOT_LESS_THAN_SIZE_MESSAGE,
    RecursiveChunkerConfig,
    SentenceChunkerConfig,
)


@pytest.mark.parametrize(
    'max_sentences, overlap, expected_message',
    [
        pytest.param(1, 2, OVERLAP_NOT_LESS_THAN_MAX_MESSAGE, id='overlap-greater-than-max'),
        pytest.param(2, 2, OVERLAP_NOT_LESS_THAN_MAX_MESSAGE, id='overlap-equal-to-max'),
        pytest.param(0, 0, MIN_MAX_SENTENCES_MESSAGE, id='max-sentences-below-one'),
        pytest.param(3, -1, MIN_OVERLAP_SENTENCES_MESSAGE, id='negative-overlap'),
    ],
)
def test_rejects_invalid_values(max_sentences: int, overlap: int, expected_message: str):
    with pytest.raises(ValueError, match=re.escape(expected_message)):
        SentenceChunkerConfig(max_sentences, overlap)


def test_accepts_valid_values():
    config = SentenceChunkerConfig(4, 2)

    assert (config.max_sentences, config.overlap_sentences) == (4, 2)


@pytest.mark.parametrize(
    'chunk_size, chunk_overlap, expected_message',
    [
        pytest.param(0, 0, MIN_CHUNK_SIZE_MESSAGE, id='chunk-size-below-one'),
        pytest.param(10, -1, MIN_CHUNK_OVERLAP_MESSAGE, id='negative-overlap'),
        pytest.param(10, 10, OVERLAP_NOT_LESS_THAN_SIZE_MESSAGE, id='overlap-equal-to-size'),
        pytest.param(10, 20, OVERLAP_NOT_LESS_THAN_SIZE_MESSAGE, id='overlap-greater-than-size'),
    ],
)
def test_recursive_config_rejects_invalid_values(chunk_size: int, chunk_overlap: int, expected_message: str):
    with pytest.raises(ValueError, match=re.escape(expected_message)):
        RecursiveChunkerConfig(chunk_size, chunk_overlap)


def test_recursive_config_accepts_valid_values():
    config = RecursiveChunkerConfig(200, 50)

    assert (config.chunk_size, config.chunk_overlap) == (200, 50)
