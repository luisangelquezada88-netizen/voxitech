"""Detector temático: orquesta carga de diccionario y detección sobre unidades."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from voxitech.topic_detection.dictionary import DictionaryLoader
from voxitech.topic_detection.matcher import DictionaryMatcher, UnitMention
from voxitech.utils.logging import get_logger

logger = get_logger()


class TopicDetector:
    """Ejecuta la detección temática completa sobre un corpus de unidades."""

    def __init__(self, dictionary_path: str | Path) -> None:
        self.dictionary_path = Path(dictionary_path)
        self.loader = DictionaryLoader()
        self.dictionary = self.loader.load(self.dictionary_path)
        self.matcher = DictionaryMatcher(self.dictionary)

    def detect_on_units(
        self,
        units_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Detecta menciones temáticas en un DataFrame de unidades.

        El DataFrame debe tener columnas: unit_id, document_id, text, word_count.
        """
        units = units_df.to_dict("records")
        mentions = self.matcher.match_units(units)

        records = []
        for m in mentions:
            records.append(
                {
                    "unit_id": m.unit_id,
                    "document_id": m.document_id,
                    "theme": m.theme,
                    "term": m.term,
                    "match_type": m.match_type,
                    "frequency": m.frequency,
                    "density_per_1k_words": m.density_per_1k_words,
                    "context_snippet": m.context_snippet,
                }
            )

        return pd.DataFrame(records)

    def get_theme_summary(self, mentions_df: pd.DataFrame) -> pd.DataFrame:
        """Resumen de menciones por tema (frecuencia total, densidad, unidades afectadas)."""
        if mentions_df.empty:
            return pd.DataFrame(columns=["theme", "total_mentions", "total_units", "avg_density_per_1k"])

        summary = (
            mentions_df.groupby("theme")
            .agg(
                total_mentions=("frequency", "sum"),
                total_units=("unit_id", "nunique"),
                avg_density_per_1k=("density_per_1k_words", "mean"),
            )
            .reset_index()
            .sort_values("total_mentions", ascending=False)
        )
        return summary

    def get_prioritized_units(
        self,
        mentions_df: pd.DataFrame,
        units_df: pd.DataFrame,
        top_n: int = 50,
    ) -> pd.DataFrame:
        """Retorna las unidades prioritarias para codificación humana.

        Prioriza por cantidad de menciones temáticas y densidad.
        """
        if mentions_df.empty:
            return pd.DataFrame()

        unit_scores = (
            mentions_df.groupby("unit_id")
            .agg(
                total_mentions=("frequency", "sum"),
                themes_count=("theme", "nunique"),
                max_density=("density_per_1k_words", "max"),
            )
            .reset_index()
        )

        # Score combinado: menciones + temas + densidad
        unit_scores["score"] = (
            unit_scores["total_mentions"] * 2
            + unit_scores["themes_count"] * 3
            + unit_scores["max_density"]
        )

        prioritized = unit_scores.sort_values("score", ascending=False).head(top_n)

        # Unir con metadatos de las unidades
        result = prioritized.merge(
            units_df[["unit_id", "document_id", "unit_index", "text", "word_count", "document_type", "date", "speaker"]],
            on="unit_id",
            how="left",
        )

        return result