"""Pruebas para el segmentador de documentos."""

from voxitech.cleaning.cleaner import CleaningResult
from voxitech.segmentation.segmenter import Segmenter


def _make_cleaning_result(text: str, document_id: str = "doc-test") -> CleaningResult:
    return CleaningResult(
        document_id=document_id,
        source_id="test_source",
        url="https://example.com/test",
        raw_file_path="data/raw/test/original.html",
        raw_hash="abc123",
        clean_file_path="data/interim/test_clean.txt",
        clean_hash="def456",
        clean_text=text,
        language="en",
        language_supported=True,
        word_count=len(text.split()),
        sentence_count=2,
        paragraph_count=1,
        boilerplate_ratio=0.1,
        cleaning_log=[],
        quality_flags=[],
    )


def test_segment_word_window():
    """Segmentación por ventana de palabras genera unidades."""
    text = " ".join(["palabra"] * 250)
    cr = _make_cleaning_result(text)
    segmenter = Segmenter(min_words=50, max_words=100)
    result = segmenter.segment_cleaning_result(cr)
    assert result.total_units >= 2
    for unit in result.units:
        assert 50 <= unit.word_count <= 100
        assert unit.unit_index >= 0
        assert unit.unit_id.startswith("doc-test") or len(unit.unit_id) > 0


def test_segment_paragraph_window():
    """Segmentación por ventana de párrafos."""
    text = "\n".join([f"Párrafo {i} con contenido suficiente para contar como párrafo válido." for i in range(6)])
    cr = _make_cleaning_result(text)
    segmenter = Segmenter(min_paragraphs=1, max_paragraphs=2, mode="paragraph_window")
    result = segmenter.segment_cleaning_result(cr)
    assert result.total_units == 3  # 2+2+2


def test_segment_has_context():
    """Cada unidad tiene prev_context y next_context."""
    text = " ".join(["palabra"] * 300)
    cr = _make_cleaning_result(text)
    segmenter = Segmenter(min_words=50, max_words=100)
    result = segmenter.segment_cleaning_result(cr)
    assert result.units[0].prev_context == ""
    assert result.units[-1].next_context == ""
    if len(result.units) > 1:
        assert result.units[1].prev_context != ""


def test_segment_deterministic_ids():
    """Los IDs de unidad son determinísticos."""
    text = " ".join(["palabra"] * 200)
    cr = _make_cleaning_result(text)
    segmenter = Segmenter(min_words=50, max_words=100)
    r1 = segmenter.segment_cleaning_result(cr)
    r2 = segmenter.segment_cleaning_result(cr)
    assert [u.unit_id for u in r1.units] == [u.unit_id for u in r2.units]


def test_segment_to_dataframe():
    """La conversión a DataFrame funciona."""
    text = " ".join(["palabra"] * 200)
    cr = _make_cleaning_result(text)
    segmenter = Segmenter(min_words=50, max_words=100)
    result = segmenter.segment_cleaning_result(cr)
    df = segmenter.to_dataframe(result)
    assert "unit_id" in df.columns
    assert "document_id" in df.columns
    assert "text" in df.columns
    assert "word_count" in df.columns
    assert len(df) == result.total_units