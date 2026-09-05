from abc import ABC, abstractmethod

from ai_rag.domain.chunking_rules import ChunkingRules
from ai_rag.domain.document_extension import DocumentExtension


class ChunkingRuleProvider(ABC):

    @abstractmethod
    def get_rules(self, extension: DocumentExtension) -> ChunkingRules:
        pass