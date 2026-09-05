import re

import pytest

from ai_rag.domain.chunking_rules import ChunkingRules
from ai_rag.domain.document_extension import DocumentExtension
from ai_rag.ingestion.chunking.rule_providers.extension_chunking_rule_provider import (
    UNSUPPORTED_EXTENSION_MESSAGE,
    ExtensionChunkingRuleProvider,
)


@pytest.fixture()
def provider() -> ExtensionChunkingRuleProvider:
    return ExtensionChunkingRuleProvider()


@pytest.mark.parametrize(
    'extension, expected_separators',
    [
        pytest.param(DocumentExtension.MARKDOWN, ('\n\n', '\n- ', '\n', '. ', ' ', ''), id='markdown'),
        pytest.param(DocumentExtension.TXT, ('\n\n', '\n', '. ', ' ', ''), id='txt'),
    ],
)
def test_returns_the_configured_rules(
    provider: ExtensionChunkingRuleProvider, extension: DocumentExtension, expected_separators: tuple[str, ...]
):
    rules = provider.get_rules(extension)

    assert rules == ChunkingRules(expected_separators)


@pytest.mark.parametrize('extension', [DocumentExtension.MARKDOWN, DocumentExtension.TXT])
def test_last_separator_is_the_empty_string(provider: ExtensionChunkingRuleProvider, extension: DocumentExtension):
    rules = provider.get_rules(extension)

    assert rules.separators[-1] == ''


def test_rejects_unsupported_extension(provider: ExtensionChunkingRuleProvider):
    with pytest.raises(NotImplementedError, match=re.escape(UNSUPPORTED_EXTENSION_MESSAGE.format(extension='pdf'))):
        provider.get_rules('pdf')
