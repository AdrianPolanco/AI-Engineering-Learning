from pathlib import Path
import structlog
from ai_rag.domain.document import Document, DocumentMetadata
from ai_rag.domain.document_extension import DocumentExtension
from ai_rag.utils.configure_logging import configure_logger

class DocumentLoader:
    def __init__(self, document_path: str):
        configure_logger()
        self.__logger = structlog.get_logger()

        # Equivalent to (not document_path.endswith('.txt') and not document_path.endswith(".md"))
        if not document_path.endswith((f'.{DocumentExtension.TXT}', f'.{DocumentExtension.MARKDOWN}')): 
            self.__logger.exception("Extension format is not valid", filename=document_path)
            raise NotImplementedError('This class only supports TXT and MD files.')
        self.__document_path = Path(document_path).resolve()

    def load(self, version: str, lang: str, document_type: str) -> Document:
        try:
            with self.__document_path.open("r", encoding="utf-8") as file:
                content = file.read()
                self.__logger.info(f'Successfully read file content at {str(self.__document_path)}')
        except FileNotFoundError:
            self.__logger.exception(f'The file {self.__document_path} does not exist.', path=str(self.__document_path))
            raise

        suffix = self.__document_path.suffix.lstrip('.').lower()
        extension = DocumentExtension(suffix)
        source =  self.__document_path.name
        document_id = self.__document_path.stem # Equivalent to source.split(".")[0]
        metadata = DocumentMetadata(source, document_type, lang, version, self.__document_path, extension)

        return Document(document_id, content, metadata)