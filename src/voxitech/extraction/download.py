"""Descarga y guarda archivos crudos con sidecar de metadatos."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from voxitech.extraction.fetcher import Fetcher, FetchResult
from voxitech.utils.hashing import sha256_bytes
from voxitech.utils.ids import document_id_from_url
from voxitech.utils.logging import get_logger

logger = get_logger()


@dataclass
class DownloadResult:
    """Resultado de descarga y guardado de un documento."""

    document_id: str
    source_id: str
    url: str
    final_url: str
    raw_file_path: str
    raw_hash: str
    meta_file_path: str
    status_code: int
    content_type: str | None
    fetched_at: str
    error: str | None = None


class Downloader:
    """Descarga documentos y los guarda en data/raw/{source_id}/ con sidecar JSON."""

    def __init__(self, raw_root: str | Path = "data/raw") -> None:
        self.raw_root = Path(raw_root)

    def _extension_from_url_or_content_type(
        self, url: str, content_type: str | None
    ) -> str:
        """Infere la extensión del archivo a partir de la URL o Content-Type."""
        parsed = Path(url)
        if parsed.suffix:
            return parsed.suffix.lower()

        if content_type:
            ct = content_type.lower()
            if "text/html" in ct:
                return ".html"
            if "application/pdf" in ct:
                return ".pdf"
            if "text/plain" in ct:
                return ".txt"
            if "application/json" in ct:
                return ".json"
            if "text/markdown" in ct:
                return ".md"

        return ".html"

    def download(self, fetcher: Fetcher, source_id: str, url: str) -> DownloadResult:
        """Descarga un documento, guarda el archivo crudo y su sidecar de metadatos."""
        result: FetchResult = fetcher.fetch(url)

        if result.error or result.status_code == 0:
            logger.error("No se pudo descargar {url}: {error}", url=url, error=result.error)
            return DownloadResult(
                document_id=document_id_from_url(url),
                source_id=source_id,
                url=url,
                final_url=result.final_url,
                raw_file_path="",
                raw_hash="",
                meta_file_path="",
                status_code=result.status_code,
                content_type=result.content_type,
                fetched_at=result.fetched_at,
                error=result.error,
            )

        document_id = document_id_from_url(url)
        ext = self._extension_from_url_or_content_type(url, result.content_type)
        source_dir = self.raw_root / source_id
        source_dir.mkdir(parents=True, exist_ok=True)

        raw_file_name = f"{document_id}_original{ext}"
        raw_file_path = source_dir / raw_file_name

        # Guardar archivo crudo (inmutable)
        raw_file_path.write_bytes(result.content)
        raw_hash = sha256_bytes(result.content)

        # Guardar sidecar de metadatos
        meta = {
            "document_id": document_id,
            "source_id": source_id,
            "url": url,
            "final_url": result.final_url,
            "status_code": result.status_code,
            "content_type": result.content_type,
            "encoding": result.encoding,
            "fetched_at": result.fetched_at,
            "raw_file": raw_file_name,
            "raw_hash": raw_hash,
            "http_headers": result.headers,
        }
        meta_file_name = f"{document_id}_meta.json"
        meta_file_path = source_dir / meta_file_name
        meta_file_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

        logger.info(
            "Descargado {url} -> {raw_file_path} (hash={raw_hash})",
            url=url,
            raw_file_path=raw_file_path,
            raw_hash=raw_hash,
        )

        return DownloadResult(
            document_id=document_id,
            source_id=source_id,
            url=url,
            final_url=result.final_url,
            raw_file_path=str(raw_file_path),
            raw_hash=raw_hash,
            meta_file_path=str(meta_file_path),
            status_code=result.status_code,
            content_type=result.content_type,
            fetched_at=result.fetched_at,
        )