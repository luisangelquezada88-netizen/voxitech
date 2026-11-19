"""Carga y validación de libros de códigos versionados (YAML)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from voxitech.utils.logging import get_logger

logger = get_logger()


@dataclass
class Code:
    """Código individual del libro de códigos (nivel 1 o 2)."""

    code_id: str
    codebook_id: str
    parent_code_id: str | None
    code: str
    label: str
    definition: str
    examples: list[str] = field(default_factory=list)
    inclusion_criteria: list[str] = field(default_factory=list)
    exclusion_criteria: list[str] = field(default_factory=list)
    level: int = 1
    memo: str | None = None


@dataclass
class CodebookConfig:
    """Configuración completa de un libro de códigos."""

    id: str
    version: str
    language: str
    project_id: str
    author: str | None
    status: str = "draft"
    description: str | None = None
    codes: list[Code] = field(default_factory=list)
    codificacion_permitida: list[str] = field(default_factory=list)
    campos_codigo: list[str] = field(default_factory=list)
    file_path: str | None = None
    file_hash: str | None = None


class CodebookLoader:
    """Carga libros de códigos desde archivos YAML."""

    def load(self, path: str | Path) -> CodebookConfig:
        """Carga un libro de códigos YAML y lo valida."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        cb_meta = data.get("codebook", {})
        codes = []
        for c in data.get("codes", []):
            codes.append(
                Code(
                    code_id=c.get("code", ""),
                    codebook_id=cb_meta.get("id", ""),
                    parent_code_id=c.get("parent_code"),
                    code=c.get("code", ""),
                    label=c.get("label", ""),
                    definition=c.get("definition", ""),
                    examples=c.get("examples", []),
                    inclusion_criteria=c.get("inclusion_criteria", []),
                    exclusion_criteria=c.get("exclusion_criteria", []),
                    level=c.get("level", 1),
                    memo=c.get("memo"),
                )
            )

        config = CodebookConfig(
            id=cb_meta.get("id", ""),
            version=cb_meta.get("version", ""),
            language=cb_meta.get("language", ""),
            project_id=cb_meta.get("project_id", ""),
            author=cb_meta.get("author"),
            status=cb_meta.get("status", "draft"),
            description=cb_meta.get("description"),
            codes=codes,
            codificacion_permitida=data.get("codificacion_permitida", []),
            campos_codigo=data.get("campos_codigo", []),
            file_path=str(path),
        )

        logger.info(
            "Libro de códigos cargado: {id} v{version} ({n_codes} códigos, nivel 1: {n_l1}, nivel 2: {n_l2})",
            id=config.id,
            version=config.version,
            n_codes=len(config.codes),
            n_l1=sum(1 for c in config.codes if c.level == 1),
            n_l2=sum(1 for c in config.codes if c.level == 2),
        )

        return config

    def get_code_by_code(self, config: CodebookConfig, code: str) -> Code | None:
        """Busca un código por su identificador corto (ej. GEN_MUJER)."""
        for c in config.codes:
            if c.code == code:
                return c
        return None

    def get_level1_codes(self, config: CodebookConfig) -> list[Code]:
        """Retorna todos los códigos de nivel 1."""
        return [c for c in config.codes if c.level == 1]

    def get_level2_codes(self, config: CodebookConfig) -> list[Code]:
        """Retorna todos los códigos de nivel 2."""
        return [c for c in config.codes if c.level == 2]

    def get_children(self, config: CodebookConfig, parent_code_id: str) -> list[Code]:
        """Retorna códigos de nivel 2 que dependen de un padre."""
        return [c for c in config.codes if c.parent_code_id == parent_code_id]