import pytest

from ai_rag.domain.document_extension import DocumentExtension
from ai_rag.ingestion.document_loader import DocumentLoader

@pytest.fixture()
def source() -> str:
    return 'example.{EXT}'

@pytest.fixture()
def file_content() -> str:
    return 'This is a test {FORMAT} document.'

@pytest.fixture()
def lang() -> str:
    return 'es'

@pytest.fixture()
def document_type() -> str:
    return 'handbook'

@pytest.fixture()
def version() -> str:
    return '1.0'

def test_load_txt_document(tmp_path, source, file_content, version, lang, document_type):
    suffix = 'txt'
    source = source.format(EXT='txt')
    file_path = tmp_path/source
    file_content = file_content.format(FORMAT='TXT')

    file_path.write_text(file_content, encoding='utf-8')

    document_loader = DocumentLoader(str(file_path))
    document = document_loader.load(version, lang, document_type)

    assert document.id == 'example'
    assert document.text == file_content
    assert document.metadata.source == source
    assert document.metadata.document_type == document_type
    assert document.metadata.lang == lang
    assert document.metadata.version == version
    assert document.metadata.path == file_path
    assert document.metadata.extension == DocumentExtension.TXT

def test_load_md_document(tmp_path, source, file_content, version, lang, document_type):
    suffix = 'md'
    source = source.replace('{EXT}', 'md')
    file_path = tmp_path/source
    file_content = file_content.replace('{FORMAT}', 'MD')

    file_path.write_text(file_content, encoding='utf-8')

    document_loader = DocumentLoader(str(file_path))
    document = document_loader.load(version, lang, document_type)

    assert document.id == 'example'
    assert document.text == file_content
    assert document.metadata.source == source
    assert document.metadata.document_type == document_type
    assert document.metadata.lang == lang
    assert document.metadata.version == version
    assert document.metadata.path == file_path
    assert document.metadata.extension == DocumentExtension.MARKDOWN

def test_rejects_unsupported_format_file(tmp_path, source):
    file_path = tmp_path/source.format(EXT='pdf')

    with pytest.raises(NotImplementedError):
        DocumentLoader(str(file_path))

def test_rejects_missing_file(version, lang, document_type):
    file_path = 'non_existent/non_existent.md'
    document_loader = DocumentLoader(file_path)

    with pytest.raises(FileNotFoundError):
        document_loader.load(version, lang, document_type)