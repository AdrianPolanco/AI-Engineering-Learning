from dataclasses import dataclass
from pathlib import Path
from ai_rag.domain.document_extension import DocumentExtension

@dataclass(frozen=True)
class DocumentMetadata:
    source: str
    document_type: str
    lang: str
    version: str
    path: Path
    extension: DocumentExtension

@dataclass(frozen=True)
class Document:
    id: str
    text: str
    metadata: DocumentMetadata