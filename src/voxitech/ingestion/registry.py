"""Registro de documentos en almacén de metadatos (SQLite)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from voxitech.utils.logging import get_logger

logger = get_logger()


class DocumentRegistry:
    """Registro de documentos ingestados en SQLite para trazabilidad y deduplicación."""

    def __init__(self, db_path: str | Path = "data/processed/metadata.sqlite") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Crea la tabla de documentos si no existe."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    source_id TEXT,
                    url TEXT,
                    final_url TEXT,
                    title TEXT,
                    document_type TEXT,
                    speaker TEXT,
                    speaker_role TEXT,
                    date TEXT,
                    attribution_type TEXT,
                    raw_file_path TEXT,
                    raw_hash TEXT,
                    meta_file_path TEXT,
                    status_code INTEGER,
                    content_type TEXT,
                    fetched_at TEXT,
                    quality_flags TEXT,
                    validation_status TEXT DEFAULT 'pending',
                    created_at TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_documents_url ON documents(url)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(raw_hash)"
            )
            conn.commit()

    def register(self, record: dict[str, Any]) -> str:
        """Registra un documento y retorna su document_id."""
        document_id = record.get("document_id")
        if not document_id:
            raise ValueError("El registro requiere un 'document_id'.")

        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO documents (
                    document_id, source_id, url, final_url, title, document_type,
                    speaker, speaker_role, date, attribution_type,
                    raw_file_path, raw_hash, meta_file_path, status_code,
                    content_type, fetched_at, quality_flags, validation_status,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    record.get("source_id"),
                    record.get("url"),
                    record.get("final_url"),
                    record.get("title"),
                    record.get("document_type"),
                    record.get("speaker"),
                    record.get("speaker_role"),
                    record.get("date"),
                    record.get("attribution_type"),
                    record.get("raw_file_path"),
                    record.get("raw_hash"),
                    record.get("meta_file_path"),
                    record.get("status_code"),
                    record.get("content_type"),
                    record.get("fetched_at"),
                    json.dumps(record.get("quality_flags", []), ensure_ascii=False),
                    record.get("validation_status", "pending"),
                    now,
                ),
            )
            conn.commit()

        logger.info("Documento registrado: {document_id}", document_id=document_id)
        return document_id

    def get_all(self) -> list[dict[str, Any]]:
        """Retorna todos los documentos registrados como diccionarios."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM documents").fetchall()
        return [dict(row) for row in rows]

    def get_by_url(self, url: str) -> dict[str, Any] | None:
        """Busca un documento por URL."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM documents WHERE url = ?", (url,)).fetchone()
        return dict(row) if row else None

    def get_by_hash(self, content_hash: str) -> dict[str, Any] | None:
        """Busca un documento por hash de contenido."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM documents WHERE raw_hash = ?", (content_hash,)
            ).fetchone()
        return dict(row) if row else None