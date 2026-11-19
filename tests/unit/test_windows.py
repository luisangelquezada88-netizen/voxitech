"""Pruebas para ventanas de segmentación."""

from voxitech.segmentation.windows import ParagraphWindow, WordWindow, sliding_context


def test_word_window_basic():
    """Divide texto en chunks de palabras."""
    window = WordWindow(min_words=5, max_words=10)
    text = " ".join(["palabra"] * 25)
    chunks = window.split(text)
    assert len(chunks) == 3  # 10 + 10 + 5
    for chunk in chunks:
        assert 5 <= len(chunk.split()) <= 10


def test_word_window_merge_small_last():
    """Fusiona último chunk si es demasiado pequeño."""
    window = WordWindow(min_words=10, max_words=10)
    text = " ".join(["palabra"] * 22)  # 10 + 10 + 2 -> último se fusiona
    chunks = window.split(text)
    assert len(chunks) == 2
    assert len(chunks[1].split()) >= 10


def test_word_window_empty():
    """Texto vacío retorna lista vacía."""
    window = WordWindow(min_words=5, max_words=10)
    assert window.split("") == []


def test_paragraph_window_basic():
    """Agrupa párrafos en unidades de hasta max_paragraphs."""
    window = ParagraphWindow(min_paragraphs=1, max_paragraphs=2)
    text = "\n".join([f"Párrafo {i}" for i in range(5)])
    chunks = window.split(text)
    assert len(chunks) == 3  # 2 + 2 + 1
    assert "Párrafo 0" in chunks[0]
    assert "Párrafo 4" in chunks[2]


def test_sliding_context_first_last():
    """Primera unidad no tiene prev, última no tiene next."""
    units = ["primera unidad", "segunda unidad", "tercera unidad"]
    ctx = sliding_context(units, context_chars=100)
    assert ctx[0]["prev_context"] == ""
    assert ctx[0]["next_context"] == "segunda unidad"
    assert ctx[2]["prev_context"] == "segunda unidad"
    assert ctx[2]["next_context"] == ""
    assert ctx[1]["text"] == "segunda unidad"


def test_sliding_context_single():
    """Una sola unidad no tiene prev ni next."""
    ctx = sliding_context(["solo una"], context_chars=100)
    assert ctx[0]["prev_context"] == ""
    assert ctx[0]["next_context"] == ""


def test_sliding_context_empty():
    """Lista vacía retorna lista vacía."""
    assert sliding_context([]) == []


def test_sliding_context_char_limit():
    """El contexto se limita a context_chars caracteres."""
    units = ["A" * 500, "B" * 500]
    ctx = sliding_context(units, context_chars=100)
    assert len(ctx[0]["next_context"]) == 100
    assert len(ctx[1]["prev_context"]) == 100