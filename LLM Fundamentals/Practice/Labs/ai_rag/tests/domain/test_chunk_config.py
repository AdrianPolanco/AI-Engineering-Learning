import re

import pytest

from ai_rag.domain.chunk_config import (
    MIN_MAX_SENTENCES_MESSAGE,
    MIN_OVERLAP_SENTENCES_MESSAGE,
    OVERLAP_NOT_LESS_THAN_MAX_MESSAGE,
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
