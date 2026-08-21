from ai_rag.domain.document import Document
from ai_rag.domain.document_extension import DocumentExtension
from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument, PreProcessedDocumentMetadata
from ai_rag.ingestion.pre_processor import DocumentPreProcessor

UNSUPPORTED_EXTENSION_MESSAGE = 'This processor only supports TXT files. You provided an {extension} file.'

class TxtPreProcessor(DocumentPreProcessor):
    def __init__(self):
        super().__init__()

    def process(self, document: Document) -> PreProcessedDocument:
        if not document.metadata.extension is DocumentExtension.TXT:
            raise NotImplementedError(UNSUPPORTED_EXTENSION_MESSAGE.format(extension=document.metadata.extension.upper()))
        unique_text_block = DocumentBlock(document.text)
        metadata = document.metadata
        pre_processed_metadata = PreProcessedDocumentMetadata(
            metadata.source,
            metadata.document_type,
            metadata.extension,
            document.id,
            metadata.lang,
            metadata.version,
            metadata.path)
        return PreProcessedDocument((unique_text_block,), pre_processed_metadata)
