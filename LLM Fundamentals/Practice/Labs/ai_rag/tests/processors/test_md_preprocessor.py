import pytest

from ai_rag.domain.document import Document
from ai_rag.domain.pre_processed_document import PreProcessedDocument
from ai_rag.ingestion.document_loader import DocumentLoader
from ai_rag.ingestion.pre_processors.md_pre_processor import MdPreProcessor


def _build_document(tmp_path, content: str, suffix: str = 'md') -> Document:
    test_path = tmp_path/f'test.{suffix}'
    test_path.write_text(content, encoding='utf-8')
    return DocumentLoader(str(test_path)).load('1.0', 'es', 'notes')


def _paths(processed: PreProcessedDocument) -> list[tuple[str, ...]]:
    return [block.heading_path for block in processed.text]


def _texts(processed: PreProcessedDocument) -> list[str]:
    return [block.text for block in processed.text]


@pytest.fixture()
def md_pre_processor() -> MdPreProcessor:
    return MdPreProcessor()


@pytest.fixture()
def txt_document(tmp_path) -> Document:
    return _build_document(tmp_path, 'Dummy content.', suffix='txt')


def test_content_under_h1(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(tmp_path, '# A\n\nContenido bajo A.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [('A',)]
    assert _texts(processed) == ['Contenido bajo A.']


def test_content_under_h1_h2(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(tmp_path, '# A\n\n## B\n\nContenido bajo B.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [('A', 'B')]


def test_content_under_h1_h2_h3_h4(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(tmp_path, '# A\n\n## B\n\n### C\n\n#### D\n\nContenido bajo D.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [('A', 'B', 'C', 'D')]


def test_transition_between_headings_of_same_level(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(
        tmp_path,
        '# A\n\n### 6. `main.py`\n\nContenido 6.\n\n### 7. `domain/document.py`\n\nContenido 7.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [
        ('A', '6. `main.py`'),
        ('A', '7. `domain/document.py`'),
    ]


def test_return_from_h4_to_h3(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(
        tmp_path,
        '# A\n\n## B\n\n### C\n\n#### D\n\nContenido D.\n\n### E\n\nContenido E.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [
        ('A', 'B', 'C', 'D'),
        ('A', 'B', 'E'),
    ]


def test_return_from_h3_to_h2(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(
        tmp_path,
        '# A\n\n## B\n\n### C\n\nContenido C.\n\n## F\n\nContenido F.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [
        ('A', 'B', 'C'),
        ('A', 'F'),
    ]


def test_full_hierarchy_example_from_spec(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(
        tmp_path,
        '# A\n## B\n### C\n#### D\n### E\n## F\nContenido F.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [('A', 'F')]


def test_content_before_first_heading(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(tmp_path, 'Contenido inicial sin heading.\n\n# A\n\nContenido bajo A.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [(), ('A',)]
    assert _texts(processed) == ['Contenido inicial sin heading.', 'Contenido bajo A.']


def test_document_without_headings(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(tmp_path, 'Solo texto plano.\n\nSin ningún heading.')

    processed = md_pre_processor.process(document)

    assert len(processed.text) == 1
    assert processed.text[0].heading_path == ()
    assert processed.text[0].text == 'Solo texto plano.\n\nSin ningún heading.'


def test_multiple_paragraphs_under_same_heading_form_a_single_block(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(
        tmp_path,
        '#### ¿Qué representa?\n\nEl entry point de la aplicación.\n\nEs donde arrancamos el sistema.')

    processed = md_pre_processor.process(document)

    assert len(processed.text) == 1
    assert processed.text[0].heading_path == ('¿Qué representa?',)
    assert processed.text[0].text == 'El entry point de la aplicación.\n\nEs donde arrancamos el sistema.'


def test_multiple_blocks_under_sibling_headings_with_same_title(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(
        tmp_path,
        '### 6. `main.py`\n\n#### ¿Qué representa?\n\nEl entry point.\n\n'
        '### 7. `domain/document.py`\n\n#### ¿Qué representa?\n\nNuestro concepto de documento.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [
        ('6. `main.py`', '¿Qué representa?'),
        ('7. `domain/document.py`', '¿Qué representa?'),
    ]
    assert _texts(processed) == ['El entry point.', 'Nuestro concepto de documento.']


def test_fenced_code_block_headings_do_not_affect_heading_path(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(
        tmp_path,
        '# A\n\n## B\n\nEjemplo:\n\n```text\n# Esto no es un heading\n## Tampoco esto\n```\n\nFin.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [('A', 'B')]
    assert _texts(processed) == [
        'Ejemplo:\n\n```text\n# Esto no es un heading\n## Tampoco esto\n```\n\nFin.'
    ]


def test_preserves_markdown_content(md_pre_processor: MdPreProcessor, tmp_path):
    content = '# A\n\n- item uno\n- item dos\n\n**negrita** y `codigo inline`.'
    document = _build_document(tmp_path, content)

    processed = md_pre_processor.process(document)

    assert processed.text[0].text == '- item uno\n- item dos\n\n**negrita** y `codigo inline`.'


def test_level_skip_from_h1_to_h3(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(tmp_path, '# A\n\n### C\n\nContenido C.')

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [('A', 'C')]


def test_headings_only_document_produces_no_blocks(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(tmp_path, '# A\n\n## B\n\n### C')

    processed = md_pre_processor.process(document)

    assert processed.text == ()


def test_full_document_from_spec(md_pre_processor: MdPreProcessor, tmp_path):
    content = (
        '# Proyecto RAG — Arquitectura y Estructura\n\n'
        '## Archivos del proyecto\n\n'
        'Introducción a los archivos del proyecto.\n\n'
        '### 6. `main.py`\n\n'
        '#### ¿Qué representa?\n\n'
        'El entry point de la aplicación.\n\n'
        '#### Responsabilidad\n\n'
        'Composición y ejecución.\n\n'
        '### 7. `domain/document.py`\n\n'
        '#### ¿Qué representa?\n\n'
        'Nuestro concepto de documento.'
    )
    document = _build_document(tmp_path, content)

    processed = md_pre_processor.process(document)

    assert _paths(processed) == [
        ('Proyecto RAG — Arquitectura y Estructura', 'Archivos del proyecto'),
        ('Proyecto RAG — Arquitectura y Estructura', 'Archivos del proyecto', '6. `main.py`', '¿Qué representa?'),
        ('Proyecto RAG — Arquitectura y Estructura', 'Archivos del proyecto', '6. `main.py`', 'Responsabilidad'),
        ('Proyecto RAG — Arquitectura y Estructura', 'Archivos del proyecto', '7. `domain/document.py`',
         '¿Qué representa?'),
    ]
    assert _texts(processed) == [
        'Introducción a los archivos del proyecto.',
        'El entry point de la aplicación.',
        'Composición y ejecución.',
        'Nuestro concepto de documento.',
    ]


def test_metadata_projection(md_pre_processor: MdPreProcessor, tmp_path):
    document = _build_document(tmp_path, '# A\n\nContenido.')

    processed = md_pre_processor.process(document)

    assert processed.metadata.document_id == document.id
    assert processed.metadata.document_type == document.metadata.document_type
    assert processed.metadata.document_version == document.metadata.version
    assert processed.metadata.document_extension == document.metadata.extension
    assert processed.metadata.document_lang == document.metadata.lang
    assert processed.metadata.document_source == document.metadata.source
    assert processed.metadata.document_path == document.metadata.path


def test_rejects_other_formats(md_pre_processor: MdPreProcessor, txt_document: Document):
    with pytest.raises(NotImplementedError):
        md_pre_processor.process(txt_document)
