"""Carga y validación de configuración del proyecto con Pydantic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    name: str
    type: str
    base_url: str | None = None
    document_types: list[str] = Field(default_factory=list)
    language: str = "en"
    active: bool = True
    rate_limit_rps: float = 1.0
    respect_robots_txt: bool = True
    user_agent: str | None = None
    selectors: dict[str, Any] = Field(default_factory=dict)


class DictionaryConfig(BaseModel):
    id: str
    path: str
    language: str
    project_id: str


class CodebookConfig(BaseModel):
    id: str
    path: str
    version: str
    language: str
    status: str = "draft"


class SegmentationConfig(BaseModel):
    mode: str = "word_window"
    min_words: int = 50
    max_words: int = 200
    min_paragraphs: int = 1
    max_paragraphs: int = 3
    context_window_chars: int = 300


class StorageConfig(BaseModel):
    corpus_format: str = "parquet"
    metadata_db: str = "data/processed/metadata.sqlite"
    raw_root: str = "data/raw"
    interim_root: str = "data/interim"
    processed_root: str = "data/processed"
    outputs_root: str = "outputs"


class DeduplicationConfig(BaseModel):
    keys: list[str] = Field(default_factory=list)
    strategy: str = "keep_first"


class QualityConfig(BaseModel):
    min_word_count_document: int = 100
    max_boilerplate_ratio: float = 0.30
    require_language_detection: bool = True
    require_date: bool = True
    blocklist_domains: list[str] = Field(default_factory=list)


class SpeakerConfig(BaseModel):
    name: str
    role: str | None = None
    attribution_rules: dict[str, str] = Field(default_factory=dict)


class TemporalConfig(BaseModel):
    start_date: str | None = None
    end_date: str | None = None
    cutoff_configurable: bool = True


class ResearchConfig(BaseModel):
    main_question: str | None = None
    themes: list[str] = Field(default_factory=list)
    theoretical_framework: str | None = None
    language: str = "en"
    languages_supported: list[str] = Field(default_factory=list)


class ProjectConfig(BaseModel):
    id: str
    name: str
    description: str
    version: str
    status: str
    created_at: str
    research: ResearchConfig
    temporal: TemporalConfig
    speaker: SpeakerConfig
    sources: list[SourceConfig]
    dictionaries: list[DictionaryConfig]
    codebook: CodebookConfig
    segmentation: SegmentationConfig
    storage: StorageConfig
    deduplication: DeduplicationConfig
    quality: QualityConfig


def load_project_config(path: str | Path) -> ProjectConfig:
    """Carga y valida un archivo YAML de configuración de proyecto."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ProjectConfig.model_validate(data)