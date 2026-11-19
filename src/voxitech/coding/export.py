"""Exportación de matriz de codificación a CSV, Parquet y Excel."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from voxitech.coding.coding import CodingStore
from voxitech.utils.logging import get_logger

logger = get_logger()


class CodingExporter:
    """Exporta la matriz de codificación a formatos abiertos."""

    def __init__(self, store: CodingStore, outputs_root: str | Path = "outputs/codificacion") -> None:
        self.store = store
        self.outputs_root = Path(outputs_root)

    def to_dataframe(self) -> Any:
        """Retorna todas las codificaciones como DataFrame."""
        return self.store.to_dataframe()

    def export_csv(self, filename: str = "codificacion.csv") -> Path:
        """Exporta a CSV."""
        self.outputs_root.mkdir(parents=True, exist_ok=True)
        path = self.outputs_root / filename
        df = self.store.to_dataframe()
        df.to_csv(path, index=False, encoding="utf-8")
        logger.info("Codificación exportada a CSV: {path} ({n} filas)", path=path, n=len(df))
        return path

    def export_parquet(self, filename: str = "codificacion.parquet") -> Path:
        """Exporta a Parquet."""
        self.outputs_root.mkdir(parents=True, exist_ok=True)
        path = self.outputs_root / filename
        df = self.store.to_dataframe()
        df.to_parquet(path, index=False)
        logger.info("Codificación exportada a Parquet: {path} ({n} filas)", path=path, n=len(df))
        return path

    def export_excel(self, filename: str = "codificacion.xlsx") -> Path:
        """Exporta a Excel (.xlsx)."""
        self.outputs_root.mkdir(parents=True, exist_ok=True)
        path = self.outputs_root / filename
        df = self.store.to_dataframe()
        df.to_excel(path, index=False, engine="openpyxl")
        logger.info("Codificación exportada a Excel: {path} ({n} filas)", path=path, n=len(df))
        return path

    def export_all(self, basename: str = "codificacion") -> dict[str, Path]:
        """Exporta a los tres formatos: CSV, Parquet, Excel."""
        return {
            "csv": self.export_csv(f"{basename}.csv"),
            "parquet": self.export_parquet(f"{basename}.parquet"),
            "excel": self.export_excel(f"{basename}.xlsx"),
        }