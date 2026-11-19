"""Ventanas de segmentación: por palabras y por párrafos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass
class WordWindow:
    """Ventana deslizante de palabras."""

    min_words: int
    max_words: int

    def split(self, text: str) -> list[str]:
        """Divide el texto en chunks de palabras entre min_words y max_words.

        Si el último chunk tiene menos de min_words palabras y hay más texto,
        se fusiona con el chunk anterior para no crear unidades demasiado pequeñas.
        """
        words = text.split()
        if not words:
            return []

        chunks: list[str] = []
        i = 0
        while i < len(words):
            chunk_words = words[i : i + self.max_words]
            chunks.append(" ".join(chunk_words))
            i += self.max_words

        # Fusionar último chunk si es demasiado pequeño y hay más de uno
        if len(chunks) > 1 and len(chunks[-1].split()) < self.min_words:
            prev = chunks.pop()
            chunks[-1] = chunks[-1] + " " + prev

        return chunks


@dataclass
class ParagraphWindow:
    """Ventana por párrafos: agrupa 1 a 3 párrafos por unidad."""

    min_paragraphs: int
    max_paragraphs: int

    def split(self, text: str) -> list[str]:
        """Divide el texto en unidades de 1 a max_paragraphs párrafos."""
        paragraphs = [p for p in text.split("\n") if p.strip()]
        if not paragraphs:
            return []

        chunks: list[str] = []
        i = 0
        while i < len(paragraphs):
            group = paragraphs[i : i + self.max_paragraphs]
            chunks.append("\n".join(group))
            i += self.max_paragraphs

        return chunks


def sliding_context(
    units: list[str], context_chars: int = 300
) -> list[dict[str, str]]:
    """Añade contexto previo y posterior a cada unidad.

    Args:
        units: Lista de textos de unidad.
        context_chars: Número de caracteres de contexto a cada lado.

    Returns:
        Lista de diccionarios con 'text', 'prev_context', 'next_context'.
    """
    result: list[dict[str, str]] = []
    total = len(units)

    for i, unit_text in enumerate(units):
        prev_text = units[i - 1] if i > 0 else ""
        next_text = units[i + 1] if i < total - 1 else ""

        # Tomar los últimos context_chars del anterior
        prev_context = prev_text[-context_chars:] if prev_text else ""
        # Tomar los primeros context_chars del siguiente
        next_context = next_text[:context_chars] if next_text else ""

        result.append(
            {
                "text": unit_text,
                "prev_context": prev_context,
                "next_context": next_context,
            }
        )

    return result