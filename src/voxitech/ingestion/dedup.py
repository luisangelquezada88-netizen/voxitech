"""Deduplicación de documentos por URL, hash de contenido y título+fecha+orador."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DedupResult:
    """Resultado de la comprobación de deduplicación."""

    is_duplicate: bool
    reason: str | None
    existing_document_id: str | None = None


class DedupChecker:
    """Comprueba si un documento ya fue ingestado basándose en claves configurables."""

    def __init__(self, keys: list[str] | None = None, strategy: str = "keep_first") -> None:
        self.keys = keys or ["url", "content_hash", "title_date_speaker"]
        self.strategy = strategy  # keep_first | keep_newest | manual_review

    def _make_title_date_speaker_key(self, record: dict[str, Any]) -> str:
        """Construye una clave estable a partir de título, fecha y orador."""
        title = str(record.get("title", "")).strip().lower()
        date = str(record.get("date", "")).strip()
        speaker = str(record.get("speaker", "")).strip().lower()
        return f"{title}|{date}|{speaker}"

    def check(
        self,
        candidate: dict[str, Any],
        existing: list[dict[str, Any]],
    ) -> DedupResult:
        """Comprueba si el candidato es duplicado de algún registro existente.

        Args:
            candidate: Metadatos del documento candidato (debe incluir url, content_hash, title, date, speaker).
            existing: Lista de registros ya ingestados.

        Returns:
            DedupResult indicando si es duplicado y por qué.
        """
        candidate_url = candidate.get("url", "")
        candidate_hash = candidate.get("content_hash", "")
        candidate_tds = self._make_title_date_speaker_key(candidate)

        for record in existing:
            if "url" in self.keys:
                if record.get("url") == candidate_url and candidate_url:
                    return DedupResult(
                        is_duplicate=True,
                        reason="duplicate_url",
                        existing_document_id=record.get("document_id"),
                    )

            if "content_hash" in self.keys:
                if record.get("content_hash") == candidate_hash and candidate_hash:
                    return DedupResult(
                        is_duplicate=True,
                        reason="duplicate_content_hash",
                        existing_document_id=record.get("document_id"),
                    )

            if "title_date_speaker" in self.keys:
                record_tds = self._make_title_date_speaker_key(record)
                if record_tds and record_tds == candidate_tds:
                    return DedupResult(
                        is_duplicate=True,
                        reason="duplicate_title_date_speaker",
                        existing_document_id=record.get("document_id"),
                    )

        return DedupResult(is_duplicate=False, reason=None)