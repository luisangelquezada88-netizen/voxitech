"""Carga y validación de diccionarios temáticos desde YAML."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from voxitech.utils.logging import get_logger

logger = get_logger()


@dataclass
class DictionaryTheme:
    """Un tema del diccionario con sus términos."""

    id: str
    label: str
    terms: list[str]
    exclusion_terms: list[str] = field(default_factory=list)


@dataclass
class DictionaryConfig:
    """Configuración completa de un diccionario temático."""

    id: str
    version: str
    language: str
    project_id: str
    description: str
    match_mode: str = "exact"
    case_sensitive: bool = False
    whole_word: bool = True
    themes: list[DictionaryTheme] = field(default_factory=list)
    notas_interpretacion: list[str] = field(default_factory=list)


class DictionaryLoader:
    """Carga diccionarios temáticos desde archivos YAML."""

    def load(self, path: str | Path) -> DictionaryConfig:
        """Carga un diccionario YAML y lo valida."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        dict_meta = data.get("dictionary", {})
        themes = []
        for t in data.get("themes", []):
            themes.append(
                DictionaryTheme(
                    id=t.get("id", ""),
                    label=t.get("label", ""),
                    terms=t.get("terms", []),
                    exclusion_terms=t.get("exclusion_terms", []),
                )
            )

        config = DictionaryConfig(
            id=dict_meta.get("id", ""),
            version=dict_meta.get("version", ""),
            language=dict_meta.get("language", ""),
            project_id=dict_meta.get("project_id", ""),
            description=dict_meta.get("description", ""),
            match_mode=dict_meta.get("match_mode", "exact"),
            case_sensitive=dict_meta.get("case_sensitive", False),
            whole_word=dict_meta.get("whole_word", True),
            themes=themes,
            notas_interpretacion=dict_meta.get("notas_interpretacion", []),
        )

        logger.info(
            "Diccionario cargado: {id} v{version} ({n_themes} temas, {n_terms} términos)",
            id=config.id,
            version=config.version,
            n_themes=len(config.themes),
            n_terms=sum(len(t.terms) for t in config.themes),
        )

        return config

    def get_terms_by_theme(self, config: DictionaryConfig, theme_id: str) -> list[str]:
        """Retorna los términos de un tema específico."""
        for theme in config.themes:
            if theme.id == theme_id:
                return theme.terms
        return []

    def get_all_theme_ids(self, config: DictionaryConfig) -> list[str]:
        """Retorna todos los IDs de tema del diccionario."""
        return [t.id for t in config.themes]