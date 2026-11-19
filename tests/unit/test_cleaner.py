"""Pruebas para el limpiador de texto."""

from voxitech.cleaning.cleaner import Cleaner


def test_cleaner_extracts_html_text():
    """Extrae texto principal de HTML eliminando scripts y estilos."""
    cleaner = Cleaner()
    html = """
    <html>
    <head><title>Test</title></head>
    <body>
        <nav>Navigation menu</nav>
        <script>console.log('hello');</script>
        <style>body { color: red; }</style>
        <main>
            <h1>Title of the speech</h1>
            <p>This is the main content of the president's speech.</p>
            <p>More important content here.</p>
        </main>
        <footer>Page footer</footer>
    </body>
    </html>
    """
    result = cleaner.clean(
        document_id="test-doc-1",
        source_id="test_source",
        url="https://example.com/test",
        raw_file_path="data/raw/test/test_original.html",
        raw_hash="abc123",
        content=html.encode("utf-8"),
        content_type="text/html",
    )

    assert "Title of the speech" in result.clean_text
    assert "main content" in result.clean_text
    assert "Navigation menu" not in result.clean_text
    assert "console.log" not in result.clean_text
    assert "color: red" not in result.clean_text
    assert "Page footer" not in result.clean_text
    assert result.word_count > 0
    assert result.language == "en"
    assert result.language_supported is True


def test_cleaner_boilerplate_ratio():
    """Calcula ratio de boilerplate para HTML."""
    cleaner = Cleaner()
    html = "<html><body><main>Contenido real</main></body></html>"
    result = cleaner.clean(
        document_id="test-doc-2",
        source_id="test_source",
        url="https://example.com/test2",
        raw_file_path="data/raw/test/test2_original.html",
        raw_hash="def456",
        content=html.encode("utf-8"),
        content_type="text/html",
    )
    assert result.boilerplate_ratio >= 0.0


def test_cleaner_no_text():
    """Documento sin texto extraído genera flag de calidad."""
    cleaner = Cleaner()
    result = cleaner.clean(
        document_id="test-doc-3",
        source_id="test_source",
        url="https://example.com/test3",
        raw_file_path="data/raw/test/test3_original.html",
        raw_hash="ghi789",
        content=b"",
        content_type="text/html",
    )
    assert "no_text_extracted" in result.quality_flags
    assert result.word_count == 0