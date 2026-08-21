import re

from ai_rag.domain.document import Document
from ai_rag.domain.document_extension import DocumentExtension
from ai_rag.domain.pre_processed_document import DocumentBlock, PreProcessedDocument, PreProcessedDocumentMetadata
from ai_rag.ingestion.pre_processor import DocumentPreProcessor

ATX_HEADING_PATTERN = re.compile(r'^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$')
CLOSING_SEQUENCE_PATTERN = re.compile(r'[ \t]+#+[ \t]*$')
FENCE_PATTERN = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
UNSUPPORTED_EXTENSION_MESSAGE = 'This processor only supports MD files. You provided an {extension} file.'


class MdPreProcessor(DocumentPreProcessor):
    def __init__(self) -> None:
        super().__init__()

    def process(self, document: Document) -> PreProcessedDocument:
        if document.metadata.extension is not DocumentExtension.MARKDOWN:
            raise NotImplementedError(
                UNSUPPORTED_EXTENSION_MESSAGE.format(extension=document.metadata.extension.upper()))

        heading_stack: list[tuple[int, str]] = []
        buffer: list[str] = []
        blocks: list[DocumentBlock] = []
        fence_delimiter: str | None = None

        def flush() -> None:
            while buffer and not buffer[0].strip():
                buffer.pop(0)
            while buffer and not buffer[-1].strip():
                buffer.pop()
            if buffer:
                heading_path = tuple(text for _, text in heading_stack)
                blocks.append(DocumentBlock('\n'.join(buffer), heading_path))
            buffer.clear()

        def push_heading(level: int, text: str) -> None:
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, text))

        for line in document.text.splitlines():
            if fence_delimiter is not None:
                buffer.append(line)
                fence_match = FENCE_PATTERN.match(line)
                if (fence_match
                        and fence_match.group(1)[0] == fence_delimiter[0]
                        and len(fence_match.group(1)) >= len(fence_delimiter)
                        and not fence_match.group(2).strip()):
                    fence_delimiter = None
                continue

            fence_match = FENCE_PATTERN.match(line)
            if fence_match:
                fence_delimiter = fence_match.group(1)
                buffer.append(line)
                continue

            heading_match = ATX_HEADING_PATTERN.match(line)
            if heading_match:
                flush()
                level = len(heading_match.group(1))
                text = CLOSING_SEQUENCE_PATTERN.sub('', heading_match.group(2) or '').strip()
                push_heading(level, text)
                continue

            buffer.append(line)

        flush()

        metadata = document.metadata
        pre_processed_metadata = PreProcessedDocumentMetadata(
            document_source=metadata.source,
            document_type=metadata.document_type,
            document_extension=metadata.extension,
            document_id=document.id,
            document_lang=metadata.lang,
            document_version=metadata.version,
            document_path=metadata.path)
        return PreProcessedDocument(tuple(blocks), pre_processed_metadata)
