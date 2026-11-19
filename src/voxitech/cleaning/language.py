"""Detección de idioma de un texto."""

from __future__ import annotations

from langdetect import detect, DetectorFactory, lang_detect_exception

# Semilla fija para detección determinística
DetectorFactory.seed = 0

SUPPORTED_LANGUAGES = {"en", "es"}


def detect_language(text: str, min_chars: int = 50) -> str:
    """Detecta el idioma de un texto.

    Args:
        text: Texto a analizar.
        min_chars: Número mínimo de caracteres para intentar detección.

    Returns:
        Código ISO 639-1 del idioma detectado, o "unknown" si no se puede determinar.
    """
    if not text or len(text.strip()) < min_chars:
        return "unknown"

    try:
        lang = detect(text)
        return lang
    except lang_detect_exception.LangDetectException:
        return "unknown"


def is_supported_language(lang: str) -> bool:
    """Indica si el idioma está soportado por el proyecto."""
    return lang in SUPPORTED_LANGUAGES