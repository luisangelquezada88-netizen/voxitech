"""Segmentador de documentos en unidades de análisis con contexto."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from voxitech.cleaning.cleaner import CleaningResult
from voxitech.segmentation.windows import ParagraphWindow, WordWindow, sliding_context
from voxitech.utils.ids import unit_id_from_document
from voxitech.utils.logging import get_logger

logger = get_logger()


@dataclass
class AnalysisUnit:
    """Unidad de análisis segmentada."""

    unit_id: str
    document_id: str
    unit_index: int
    text: str
    word_count: int
    prev_context: str
    next_context: str
    segment_type: str  # word_window | paragraph_window
    char_start: int
    char_end: int
    document_type: str | None = None
    date: str | None = None
    speaker: str | None = None


@dataclass
class SegmentationResult:
    """Resultado de segmentación de un documento."""

    document_id: str
    units: list[AnalysisUnit] = field(default_factory=list)
    total_units: int = 0
    mode: str = "word_window"
    log: list[str] = field(default_factory=list)


class Segmenter:
    """Segmenta documentos limpios en unidades de análisis."""

    def __init__(
        self,
        min_words: int = 50,
        max_words: int = 200,
        min_paragraphs: int = 1,
        max_paragraphs: int = 3,
        context_window_chars: int = 300,
        mode: str = "word_window",
    ) -> None:
        self.min_words = min_words
        self.max_words = max_words
        self.min_paragraphs = min_paragraphs
        self.max_paragraphs = max_paragraphs
        self.context_window_chars = context_window_chars
        self.mode = mode  # word_window | paragraph_window | both

    def segment_cleaning_result(
        self,
        cleaning_result: CleaningResult,
        document_type: str | None = None,
        date: str | None = None,
        speaker: str | None = None,
    ) -> SegmentationResult:
        """Segmenta un CleaningResult en unidades de análisis."""
        log: list[str] = []
        clean_text = cleaning_result.clean_text
        document_id = cleaning_result.document_id

        if not clean_text:
            log.append("Documento sin texto limpio; no se generaron unidades")
            return SegmentationResult(
                document_id=document_id,
                units=[],
                total_units=0,
                mode=self.mode,
                log=log,
            )

        all_unit_texts: list[str] = []

        if self.mode == "word_window":
            window = WordWindow(min_words=self.min_words, max_words=self.max_words)
            all_unit_texts = window.split(clean_text)
            log.append(f"Segmentación por palabra: {len(all_unit_texts)} unidades")

        elif self.mode == "paragraph_window":
            window = ParagraphWindow(
                min_paragraphs=self.min_paragraphs, max_paragraphs=self.max_paragraphs
            )
            all_unit_texts = window.split(clean_text)
            log.append(f"Segmentación por párrafo: {len(all_unit_texts)} unidades")

        elif self.mode == "both":
            word_window = WordWindow(min_words=self.min_words, max_words=self.max_words)
            para_window = ParagraphWindow(
                min_paragraphs=self.min_paragraphs, max_paragraphs=self.max_paragraphs
            )
            word_units = word_window.split(clean_text)
            para_units = para_window.split(clean_text)
            # Combinar sin duplicados exactos
            seen = set()
            for u in word_units + para_units:
                if u not in seen:
                    all_unit_texts.append(u)
                    seen.add(u)
            log.append(
                f"Segmentación mixta: {len(word_units)} por palabra + "
                f"{len(para_units)} por párrafo = {len(all_unit_texts)} unidades únicas"
            )
        else:
            raise ValueError(f"Modo de segmentación desconocido: {self.mode}")

        # Añadir contexto previo/posterior
        contextualized = sliding_context(
            all_unit_texts, context_chars=self.context_window_chars
        )

        units: list[AnalysisUnit] = []
        char_offset = 0
        for i, ctx in enumerate(contextualized):
            unit_text = ctx["text"]
            unit_id = unit_id_from_document(document_id, i)
            char_start = char_offset
            char_end = char_offset + len(unit_text)
            char_offset = char_end

            unit = AnalysisUnit(
                unit_id=unit_id,
                document_id=document_id,
                unit_index=i,
                text=unit_text,
                word_count=len(unit_text.split()),
                prev_context=ctx["prev_context"],
                next_context=ctx["next_context"],
                segment_type=self.mode,
                char_start=char_start,
                char_end=char_end,
                document_type=document_type,
                date=date,
                speaker=speaker,
            )
            units.append(unit)

        log.append(f"Unidades con contexto generadas: {len(units)}")

        return SegmentationResult(
            document_id=document_id,
            units=units,
            total_units=len(units),
            mode=self.mode,
            log=log,
        )

    def to_dataframe(self, result: SegmentationResult) -> pd.DataFrame:
        """Convierte un SegmentationResult a DataFrame de pandas."""
        records = []
        for unit in result.units:
            records.append(
                {
                    "unit_id": unit.unit_id,
                    "document_id": unit.document_id,
                    "unit_index": unit.unit_index,
                    "text": unit.text,
                    "word_count": unit.word_count,
                    "prev_context": unit.prev_context,
                    "next_context": unit.next_context,
                    "segment_type": unit.segment_type,
                    "char_start": unit.char_start,
                    "char_end": unit.char_end,
                    "document_type": unit.document_type,
                    "date": unit.date,
                    "speaker": unit.speaker,
                }
            )
        return pd.DataFrame(records)