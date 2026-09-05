from ai_rag.domain.chunking_rules import ChunkingRules
from ai_rag.domain.document_extension import DocumentExtension
from ai_rag.ingestion.chunking.chunking_rule_provider import ChunkingRuleProvider

UNSUPPORTED_EXTENSION_MESSAGE = 'No chunking rules are configured for extension {extension}.'

_RULES_BY_EXTENSION: dict[DocumentExtension, ChunkingRules] = {
    DocumentExtension.MARKDOWN: ChunkingRules(('\n\n', '\n- ', '\n', '. ', ' ', '')),
    DocumentExtension.TXT: ChunkingRules(('\n\n', '\n', '. ', ' ', '')),
}


class ExtensionChunkingRuleProvider(ChunkingRuleProvider):
    def get_rules(self, extension: DocumentExtension) -> ChunkingRules:
        try:
            return _RULES_BY_EXTENSION[extension]
        except KeyError:
            raise NotImplementedError(UNSUPPORTED_EXTENSION_MESSAGE.format(extension=extension)) from None
