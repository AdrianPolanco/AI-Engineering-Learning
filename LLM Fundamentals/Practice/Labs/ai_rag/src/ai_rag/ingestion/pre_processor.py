from abc import ABC, abstractmethod

from ai_rag.domain.document import Document
from ai_rag.domain.pre_processed_document import PreProcessedDocument

class DocumentPreProcessor(ABC):

    @abstractmethod
    def process(self, document: Document) -> PreProcessedDocument:
        pass