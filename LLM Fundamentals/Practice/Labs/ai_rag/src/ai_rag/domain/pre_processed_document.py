from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class PreProcessedDocumentMetadata:
    document_source: str
    document_type: str
    document_extension: str
    document_id: str
    document_lang: str
    document_version: str
    document_path: Path

@dataclass(frozen=True)
class DocumentBlock:
    text: str
    # tuple[str, ...] declara una tupla con un str y una cantidad indeterminada de elementos
    heading_path: tuple[str, ...] = ()

@dataclass(frozen=True)
class PreProcessedDocument:
    text: tuple[DocumentBlock, ...]
    metadata: PreProcessedDocumentMetadata