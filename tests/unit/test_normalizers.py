"""Pruebas para normalizadores de texto."""

from voxitech.cleaning.normalizers import (
    normalize_whitespace,
    normalize_quotes,
    normalize_dashes,
    normalize_encoding,
    normalize_text,
)


def test_normalize_whitespace():
    """Colapsa múltiples espacios y saltos de línea."""
    assert normalize_whitespace("hola   mundo") == "hola mundo"
    assert normalize_whitespace("línea1\n\n\nlínea2") == "línea1\n\nlínea2"
    assert normalize_whitespace("  tab\t\tado  ") == "tab ado"


def test_normalize_quotes():
    """Convierte comillas tipográficas a ASCII."""
    assert normalize_quotes("\u201chola\u201d") == '"hola"'
    assert normalize_quotes("\u2018mundo\u2019") == "'mundo'"
    assert normalize_quotes("texto sin comillas") == "texto sin comillas"


def test_normalize_dashes():
    """Convierte rayas y guiones tipográficos a guion ASCII."""
    assert normalize_dashes("\u2014") == "-"
    assert normalize_dashes("\u2013") == "-"
    assert normalize_dashes("a\u2012b") == "a-b"


def test_normalize_encoding():
    """Elimina caracteres de control e invisibles."""
    assert normalize_encoding("\ufeffhola\u200bmundo") == "hola mundo"
    assert normalize_encoding("texto normal") == "texto normal"
    assert normalize_encoding("palabra\u2060otra") == "palabra otra"


def test_normalize_text_pipeline():
    """El pipeline completo aplica todos los normalizadores en orden."""
    sucio = '\u201cHola\u201d   mundo\u2014ejemplo\ufeff'
    limpio = normalize_text(sucio)
    assert "\u201c" not in limpio
    assert "\u201d" not in limpio
    assert "\ufeff" not in limpio
    assert "\u2014" not in limpio
    assert "   " not in limpio  # sin espacios múltiples


def test_normalize_text_empty():
    """Texto vacío no lanza excepción."""
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""