"""Análisis cuantitativo y generación de gráficos del discurso de género."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from voxitech.utils.logging import get_logger

logger = get_logger()


class DiscourseAnalyzer:
    """Análisis cuantitativo de menciones temáticas y codificaciones."""

    def __init__(self, outputs_root: str | Path = "outputs/analisis") -> None:
        self.outputs_root = Path(outputs_root)
        self.outputs_root.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid")

    # ------------------------------------------------------------------
    # Métricas por tema
    # ------------------------------------------------------------------
    def theme_frequency(self, mentions_df: pd.DataFrame) -> pd.DataFrame:
        """Frecuencia total de menciones por tema."""
        if mentions_df.empty:
            return pd.DataFrame(columns=["theme", "total_mentions", "total_units"])
        return (
            mentions_df.groupby("theme")
            .agg(total_mentions=("frequency", "sum"), total_units=("unit_id", "nunique"))
            .reset_index()
            .sort_values("total_mentions", ascending=False)
        )

    def theme_density(self, mentions_df: pd.DataFrame) -> pd.DataFrame:
        """Densidad promedio por tema (menciones por 1.000 palabras)."""
        if mentions_df.empty:
            return pd.DataFrame(columns=["theme", "avg_density_per_1k"])
        return (
            mentions_df.groupby("theme")["density_per_1k_words"]
            .mean()
            .reset_index()
            .rename(columns={"density_per_1k_words": "avg_density_per_1k"})
            .sort_values("avg_density_per_1k", ascending=False)
        )

    # ------------------------------------------------------------------
    # Gráficos
    # ------------------------------------------------------------------
    def plot_theme_frequency(
        self, mentions_df: pd.DataFrame, filename: str = "frecuencia_por_tema.png"
    ) -> Path:
        """Barras horizontales de frecuencia de menciones por tema."""
        summary = self.theme_frequency(mentions_df)
        if summary.empty:
            logger.warning("No hay datos para graficar frecuencia por tema")
            return self.outputs_root / filename

        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=summary,
            x="total_mentions",
            y="theme",
            hue="theme",
            palette="viridis",
            orient="h",
            legend=False,
        )
        plt.title("Frecuencia de menciones temáticas por tema")
        plt.xlabel("Número de menciones")
        plt.ylabel("Tema")
        plt.tight_layout()
        path = self.outputs_root / filename
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info("Gráfico guardado: {path}", path=path)
        return path

    def plot_theme_density(
        self, mentions_df: pd.DataFrame, filename: str = "densidad_por_tema.png"
    ) -> Path:
        """Barras de densidad promedio por tema."""
        summary = self.theme_density(mentions_df)
        if summary.empty:
            logger.warning("No hay datos para graficar densidad por tema")
            return self.outputs_root / filename

        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=summary,
            x="avg_density_per_1k",
            y="theme",
            hue="theme",
            palette="mako",
            orient="h",
            legend=False,
        )
        plt.title("Densidad promedio de menciones por tema (por 1.000 palabras)")
        plt.xlabel("Densidad promedio (menciones / 1.000 palabras)")
        plt.ylabel("Tema")
        plt.tight_layout()
        path = self.outputs_root / filename
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info("Gráfico guardado: {path}", path=path)
        return path

    def plot_mentions_over_time(
        self, mentions_df: pd.DataFrame, units_df: pd.DataFrame, filename: str = "menciones_por_fecha.png"
    ) -> Path:
        """Evolución temporal de menciones temáticas."""
        if mentions_df.empty or units_df.empty or "date" not in units_df.columns:
            logger.warning("Datos insuficientes para serie temporal")
            return self.outputs_root / filename

        merged = mentions_df.merge(units_df[["unit_id", "date"]], on="unit_id", how="left")
        merged = merged.dropna(subset=["date"])
        if merged.empty:
            logger.warning("Sin fechas para graficar serie temporal")
            return self.outputs_root / filename

        merged["date"] = pd.to_datetime(merged["date"], errors="coerce")
        merged = merged.dropna(subset=["date"])
        time_series = (
            merged.groupby([merged["date"].dt.date, "theme"])["frequency"]
            .sum()
            .reset_index()
        )

        plt.figure(figsize=(12, 6))
        sns.lineplot(
            data=time_series,
            x="date",
            y="frequency",
            hue="theme",
            marker="o",
        )
        plt.title("Evolución de menciones temáticas en el tiempo")
        plt.xlabel("Fecha")
        plt.ylabel("Menciones")
        plt.xticks(rotation=45)
        plt.tight_layout()
        path = self.outputs_root / filename
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info("Gráfico guardado: {path}", path=path)
        return path

    def plot_coding_status(
        self, coding_df: pd.DataFrame, filename: str = "estado_codificacion.png"
    ) -> Path:
        """Barras de estado de las codificaciones."""
        if coding_df.empty or "status" not in coding_df.columns:
            logger.warning("No hay datos de codificación para graficar")
            return self.outputs_root / filename

        counts = coding_df["status"].value_counts().reset_index()
        counts.columns = ["status", "count"]

        plt.figure(figsize=(7, 5))
        sns.barplot(data=counts, x="status", y="count", hue="status", palette="Set2", legend=False)
        plt.title("Estado de las codificaciones (revisión humana)")
        plt.xlabel("Estado")
        plt.ylabel("Número de codificaciones")
        plt.tight_layout()
        path = self.outputs_root / filename
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info("Gráfico guardado: {path}", path=path)
        return path

    # ------------------------------------------------------------------
    # Métricas del corpus
    # ------------------------------------------------------------------
    def corpus_stats(self, units_df: pd.DataFrame, mentions_df: pd.DataFrame) -> dict[str, Any]:
        """Estadísticas globales del corpus analizado."""
        stats: dict[str, Any] = {}
        stats["total_units"] = int(len(units_df))
        stats["total_words"] = int(units_df["word_count"].sum()) if "word_count" in units_df.columns else 0
        stats["total_mentions"] = int(mentions_df["frequency"].sum()) if not mentions_df.empty else 0
        stats["themes_detected"] = int(mentions_df["theme"].nunique()) if not mentions_df.empty else 0
        stats["units_with_mentions"] = int(mentions_df["unit_id"].nunique()) if not mentions_df.empty else 0
        return stats
