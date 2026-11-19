"""Normalizadores de texto: espacios, saltos de línea, comillas, guiones, codificación UTF-8."""

from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    """Normaliza espacios en blanco, saltos de línea y tabulaciones a un solo espacio."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text


def normalize_quotes(text: str) -> str:
    """Normaliza comillas tipográficas y rectas a comillas ASCII estándar."""
    replacements = {
        "\u201c": '"',  # left double quotation mark
        "\u201d": '"',  # right double quotation mark
        "\u2018": "'",  # left single quotation mark
        "\u2019": "'",  # right single quotation mark / apostrophe
        "\u201a": "'",  # single low-9 quotation mark
        "\u201e": '"',  # double low-9 quotation mark
        "\u00ab": '"',  # left-pointing double angle quotation mark
        "\u00bb": '"',  # right-pointing double angle quotation mark
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def normalize_dashes(text: str) -> str:
    """Normaliza guiones y rayas tipográficos a guion ASCII estándar."""
    replacements = {
        "\u2012": "-",  # figure dash
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2015": "-",  # horizontal bar
        "\u2212": "-",  # minus sign
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def normalize_encoding(text: str) -> str:
    """Asegura que el texto esté en UTF-8 y elimina caracteres de control invisibles."""
    # Eliminar caracteres de control excepto saltos de línea y tabulaciones
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    # Reemplazar caracteres no imprimibles comunes
    text = text.replace("\ufeff", "")  # BOM
    text = text.replace("\u200b", " ")  # zero-width space -> espacio
    text = text.replace("\u200c", "")  # zero-width non-joiner
    text = text.replace("\u200d", "")  # zero-width joiner
    text = text.replace("\u2060", " ")  # word joiner -> espacio
    return text


def normalize_text(text: str) -> str:
    """Aplica todos los normalizadores en orden seguro."""
    text = normalize_encoding(text)
    text = normalize_quotes(text)
    text = normalize_dashes(text)
    text = normalize_whitespace(text)
    return text