"""Motor de coincidencias temáticas por diccionario."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from voxitech.topic_detection.dictionary import DictionaryConfig, DictionaryTheme
from voxitech.utils.logging import get_logger

logger = get_logger()


@dataclass
class MatchResult:
    """Resultado de una coincidencia temática."""

    theme_id: str
    theme_label: str
    term: str
    match_type: str  # exact | regex | lemma
    frequency: int
    density_per_1k_words: float
    context_snippet: str
    unit_id: str


@dataclass
class UnitMention:
    """Menciones temáticas de una unidad."""

    unit_id: str
    document_id: str
    theme: str
    term: str
    match_type: str
    frequency: int
    density_per_1k_words: float
    context_snippet: str


class DictionaryMatcher:
    """Busca términos del diccionario en texto y calcula frecuencia y densidad."""

    def __init__(self, dictionary: DictionaryConfig) -> None:
        self.dictionary = dictionary
        self.theme_map: dict[str, DictionaryTheme] = {
            t.id: t for t in dictionary.themes
        }

    def _build_pattern(self, term: str) -> re.Pattern:
        """Construye un patrón regex para un término según la configuración."""
        if self.dictionary.case_sensitive:
            flags = 0
        else:
            flags = re.IGNORECASE

        if self.dictionary.whole_word:
            pattern = r"\b" + re.escape(term) + r"\b"
        else:
            pattern = re.escape(term)

        return re.compile(pattern, flags)

    def count_matches(self, text: str, term: str) -> int:
        """Cuenta coincidencias de un término en un texto."""
        pattern = self._build_pattern(term)
        return len(pattern.findall(text))

    def get_context_snippet(
        self, text: str, term: str, window_chars: int = 100
    ) -> str:
        """Extrae un snippet de contexto alrededor de la primera coincidencia."""
        pattern = self._build_pattern(term)
        match = pattern.search(text)
        if not match:
            return ""
        start = max(0, match.start() - window_chars)
        end = min(len(text), match.end() + window_chars)
        return text[start:end].strip()

    def match_unit(
        self,
        unit_id: str,
        document_id: str,
        text: str,
        word_count: int,
    ) -> list[UnitMention]:
        """Detecta menciones temáticas en una unidad de análisis."""
        mentions: list[UnitMention] = []
        text_for_match = text if self.dictionary.case_sensitive else text.lower()

        for theme in self.dictionary.themes:
            for term in theme.terms:
                term_for_match = term if self.dictionary.case_sensitive else term.lower()
                frequency = self.count_matches(text_for_match, term_for_match)

                if frequency > 0:
                    density = (frequency / word_count) * 1000 if word_count > 0 else 0.0
                    snippet = self.get_context_snippet(text, term)
                    mentions.append(
                        UnitMention(
                            unit_id=unit_id,
                            document_id=document_id,
                            theme=theme.id,
                            term=term,
                            match_type=self.dictionary.match_mode,
                            frequency=frequency,
                            density_per_1k_words=round(density, 4),
                            context_snippet=snippet,
                        )
                    )

        return mentions

    def match_units(
        self,
        units: list[dict[str, Any]],
    ) -> list[UnitMention]:
        """Detecta menciones en una lista de unidades (dicts con unit_id, document_id, text, word_count)."""
        all_mentions: list[UnitMention] = []
        for unit in units:
            mentions = self.match_unit(
                unit_id=unit["unit_id"],
                document_id=unit["document_id"],
                text=unit["text"],
                word_count=unit.get("word_count", len(unit["text"].split())),
            )
            all_mentions.extend(mentions)

        logger.info(
            "Detección temática completada: {n_mentions} menciones en {n_units} unidades",
            n_mentions=len(all_mentions),
            n_units=len(units),
        )

        return all_mentions