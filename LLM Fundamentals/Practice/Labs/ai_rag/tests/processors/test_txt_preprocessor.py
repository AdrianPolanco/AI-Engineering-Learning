import pytest

from ai_rag.domain.document import Document
from ai_rag.ingestion.document_loader import DocumentLoader
from ai_rag.ingestion.pre_processors.txt_pre_processor import TxtPreProcessor


@pytest.fixture()
def txt_document(tmp_path) -> Document:
    test_path = tmp_path/'test.txt'
    test_path.write_text('''Lorem Ipsum is simply dummy text of the printing and typesetting industry. 
    Lorem Ipsum has been the industry's standard dummy text ever since 1966, when designers at Letraset 
    and James Mosley, the librarian at St Bride Printing Library in London, 
    took a 1914 Cicero translation and scrambled it to make dummy text for Letraset's Body Type sheets. 
    It has survived not only many decades, but also the leap into electronic typesetting, 
    remaining essentially unchanged. It was popularised thanks to these sheets and more recently 
    with desktop publishing software like Aldus PageMaker and Microsoft Word including versions of
    Lorem Ipsum.''', encoding='utf-8')
    return DocumentLoader(str(test_path)).load('1.0', 'es', 'history')

@pytest.fixture()
def md_document(tmp_path) -> Document:
    test_path = tmp_path/'test.md'
    test_path.write_text('This is just a dummy file.')
    return DocumentLoader(str(test_path)).load('1.0', 'es', 'test')


@pytest.fixture(scope='session') 
def txt_pre_processor()-> TxtPreProcessor:
    return TxtPreProcessor()

def test_processor_generates_a_single_headless_block(txt_pre_processor: TxtPreProcessor, txt_document: Document):
    processed_doc = txt_pre_processor.process(txt_document)

    assert len(processed_doc.text) == 1
    assert len(processed_doc.text[0].heading_path) == 0

def test_document_block_data(txt_pre_processor: TxtPreProcessor, txt_document: Document):
    processed_doc = txt_pre_processor.process(txt_document)

    assert processed_doc.text[0].text == txt_document.text
    assert processed_doc.metadata.document_id == txt_document.id
    assert processed_doc.metadata.document_type == txt_document.metadata.document_type
    assert processed_doc.metadata.document_version == txt_document.metadata.version
    assert processed_doc.metadata.document_extension == txt_document.metadata.extension
    assert processed_doc.metadata.document_lang == txt_document.metadata.lang
    assert processed_doc.metadata.document_source == txt_document.metadata.source
    assert processed_doc.metadata.document_path == txt_document.metadata.path

def test_rejects_other_formats(txt_pre_processor: TxtPreProcessor, md_document: Document):
    with pytest.raises(NotImplementedError):
        txt_pre_processor.process(md_document)