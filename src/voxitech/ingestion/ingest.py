"""Orquestador de ingesta: extracción -> deduplicación -> registro."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from voxitech.extraction.download import DownloadResult, Downloader
from voxitech.extraction.fetcher import Fetcher
from voxitech.ingestion.dedup import DedupChecker
from voxitech.ingestion.registry import DocumentRegistry
from voxitech.utils.logging import get_logger

logger = get_logger()


class Ingester:
    """Orquesta la ingesta completa de un documento desde una fuente."""

    def __init__(
        self,
        fetcher: Fetcher,
        downloader: Downloader,
        dedup: DedupChecker,
        registry: DocumentRegistry,
    ) -> None:
        self.fetcher = fetcher
        self.downloader = downloader
        self.dedup = dedup
        self.registry = registry

    def ingest_source_document(
        self,
        source_id: str,
        document_meta: dict[str, Any],
    ) -> dict[str, Any]:
        """Ingesta un documento individual desde sus metadatos de configuración.

        Args:
            source_id: Identificador de la fuente.
            document_meta: Diccionario con al menos url, title, document_type, speaker, date, attribution_type.

        Returns:
            Diccionario con el resultado de la ingesta (documento registrado o duplicado).
        """
        url = document_meta["url"]
        logger.info("Iniciando ingesta de {url}", url=url)

        # 1. Verificar duplicados en el registro existente
        existing = self.registry.get_all()
        candidate_for_dedup = {
            "url": url,
            "content_hash": "",  # Se calcula tras descarga
            "title": document_meta.get("title", ""),
            "date": document_meta.get("date", ""),
            "speaker": document_meta.get("speaker", ""),
        }

        # Comprobación rápida por URL antes de descargar
        if "url" in self.dedup.keys:
            existing_by_url = self.registry.get_by_url(url)
            if existing_by_url:
                logger.warning("Duplicado por URL, saltando descarga: {url}", url=url)
                return {
                    "document_id": existing_by_url["document_id"],
                    "status": "skipped_duplicate",
                    "reason": "duplicate_url",
                    "source_id": source_id,
                    "url": url,
                }

        # 2. Descargar archivo crudo
        download_result: DownloadResult = self.downloader.download(
            self.fetcher, source_id, url
        )

        if download_result.error:
            logger.error("Fallo en descarga de {url}: {error}", url=url, error=download_result.error)
            return {
                "document_id": download_result.document_id,
                "status": "failed",
                "reason": download_result.error,
                "source_id": source_id,
                "url": url,
            }

        # 3. Comprobación de deduplicación por hash de contenido tras descarga
        candidate_for_dedup["content_hash"] = download_result.raw_hash
        dedup_result = self.dedup.check(candidate_for_dedup, existing)
        if dedup_result.is_duplicate:
            logger.warning(
                "Duplicado detectado ({reason}), saltando registro: {url}",
                reason=dedup_result.reason,
                url=url,
            )
            return {
                "document_id": dedup_result.existing_document_id or download_result.document_id,
                "status": "skipped_duplicate",
                "reason": dedup_result.reason,
                "source_id": source_id,
                "url": url,
                "raw_file_path": download_result.raw_file_path,
                "raw_hash": download_result.raw_hash,
            }

        # 4. Construir registro completo
        full_record: dict[str, Any] = {
            "document_id": download_result.document_id,
            "source_id": source_id,
            "url": url,
            "final_url": download_result.final_url,
            "title": document_meta.get("title", ""),
            "document_type": document_meta.get("document_type", "other"),
            "speaker": document_meta.get("speaker", ""),
            "speaker_role": document_meta.get("speaker_role", ""),
            "date": document_meta.get("date", ""),
            "attribution_type": document_meta.get("attribution_type", "contextual_material"),
            "raw_file_path": download_result.raw_file_path,
            "raw_hash": download_result.raw_hash,
            "meta_file_path": download_result.meta_file_path,
            "status_code": download_result.status_code,
            "content_type": download_result.content_type,
            "fetched_at": download_result.fetched_at,
            "quality_flags": [],
            "validation_status": "pending",
        }

        # 5. Registrar en SQLite
        self.registry.register(full_record)

        return {
            "document_id": download_result.document_id,
            "status": "ingested",
            "reason": None,
            "source_id": source_id,
            "url": url,
            "raw_file_path": download_result.raw_file_path,
            "raw_hash": download_result.raw_hash,
        }

    def ingest_sources_config(self, sources_config: dict[str, Any]) -> list[dict[str, Any]]:
        """Ingesta todos los documentos listados en la configuración de fuentes.

        Args:
            sources_config: Diccionario con claves 'sources' y 'documents' como en config/sources/white_house.yaml.

        Returns:
            Lista de resultados de ingesta por documento.
        """
        results: list[dict[str, Any]] = []
        documents = sources_config.get("documents", [])
        logger.info("Iniciando ingesta de {n} documentos", n=len(documents))

        for doc in documents:
            source_id = doc.get("source_id", "unknown")
            result = self.ingest_source_document(source_id, doc)
            results.append(result)

        return results