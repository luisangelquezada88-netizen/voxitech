"""Pruebas para detección de idioma."""

from voxitech.cleaning.language import detect_language, is_supported_language


def test_detect_english():
    """Detecta inglés correctamente."""
    lang = detect_language("The quick brown fox jumps over the lazy dog. This is a longer English sentence to ensure reliable language detection by the algorithm.")
    assert lang == "en"


def test_detect_spanish():
    """Detecta español correctamente."""
    lang = detect_language("El veloz zorro marrón salta sobre el perro perezoso.")
    assert lang == "es"


def test_detect_unknown_short_text():
    """Texto muy corto retorna unknown."""
    lang = detect_language("hi")
    assert lang == "unknown"


def test_detect_unknown_empty():
    """Texto vacío retorna unknown."""
    lang = detect_language("")
    assert lang == "unknown"


def test_is_supported_language():
    """Valida idiomas soportados."""
    assert is_supported_language("en") is True
    assert is_supported_language("es") is True
    assert is_supported_language("fr") is False
    assert is_supported_language("unknown") is False