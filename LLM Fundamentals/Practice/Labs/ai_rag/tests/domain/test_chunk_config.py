import re

import pytest

from ai_rag.domain.chunk_config import (
    INVALID_BREAKPOINT_PERCENTILE_MESSAGE,
    MIN_CHUNK_OVERLAP_MESSAGE,
    MIN_CHUNK_SIZE_MESSAGE,
    MIN_CHUNK_SIZE_NOT_LESS_THAN_MAX_MESSAGE,
    MIN_MAX_CHUNK_SIZE_MESSAGE,
    MIN_MAX_SENTENCES_MESSAGE,
    MIN_MIN_CHUNK_SIZE_MESSAGE,
    MIN_OVERLAP_SENTENCES_MESSAGE,
    MIN_OVERLAP_SIZE_MESSAGE,
    OVERLAP_NOT_LESS_THAN_MAX_MESSAGE,
    OVERLAP_NOT_LESS_THAN_SIZE_MESSAGE,
    SEMANTIC_OVERLAP_NOT_LESS_THAN_MAX_MESSAGE,
    RecursiveChunkerConfig,
    SemanticChunkerConfig,
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


@pytest.mark.parametrize(
    'max_chunk_size, min_chunk_size, overlap_size, breakpoint_percentile_threshold, expected_message',
    [
        pytest.param(0, 1, 0, 95.0, MIN_MAX_CHUNK_SIZE_MESSAGE, id='max-chunk-size-below-one'),
        pytest.param(10, 0, 0, 95.0, MIN_MIN_CHUNK_SIZE_MESSAGE, id='min-chunk-size-below-one'),
        pytest.param(10, 10, 0, 95.0, MIN_CHUNK_SIZE_NOT_LESS_THAN_MAX_MESSAGE, id='min-chunk-size-equal-to-max'),
        pytest.param(10, 5, 10, 95.0, SEMANTIC_OVERLAP_NOT_LESS_THAN_MAX_MESSAGE, id='overlap-equal-to-max'),
        pytest.param(10, 5, -1, 95.0, MIN_OVERLAP_SIZE_MESSAGE, id='negative-overlap'),
        pytest.param(10, 5, 2, 101, INVALID_BREAKPOINT_PERCENTILE_MESSAGE, id='breakpoint-above-100'),
    ],
)
def test_semantic_config_rejects_invalid_values(
    max_chunk_size: int,
    min_chunk_size: int,
    overlap_size: int,
    breakpoint_percentile_threshold: float,
    expected_message: str,
):
    with pytest.raises(ValueError, match=re.escape(expected_message)):
        SemanticChunkerConfig(max_chunk_size, min_chunk_size, overlap_size, breakpoint_percentile_threshold)


def test_semantic_config_accepts_valid_values():
    config = SemanticChunkerConfig(1200, 200, 100)

    assert (config.max_chunk_size, config.min_chunk_size, config.overlap_size) == (1200, 200, 100)
    assert config.breakpoint_percentile_threshold == 95.0
