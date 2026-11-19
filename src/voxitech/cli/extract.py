"""Comando CLI de extracción de documentos desde fuentes configuradas."""

from __future__ import annotations

import typer
from pathlib import Path
from typing import Optional

from voxitech.extraction.download import Downloader
from voxitech.extraction.fetcher import Fetcher
from voxitech.ingestion.dedup import DedupChecker
from voxitech.ingestion.ingest import Ingester
from voxitech.ingestion.registry import DocumentRegistry
from voxitech.utils.logging import configure_logging, get_logger

logger = get_logger()


def extract_command(
    config_path: str = typer.Argument("config/sources/white_house.yaml", help="Ruta al YAML de configuración de fuentes"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Solo muestra qué se descargaría sin ejecutar peticiones HTTP"),
    log_level: str = typer.Option("INFO", "--log-level", help="Nivel de logging"),
) -> None:
    """Ejecuta la extracción e ingesta de documentos desde un archivo de configuración de fuentes."""
    configure_logging(level=log_level)

    import yaml

    config_file = Path(config_path)
    if not config_file.exists():
        logger.error("Archivo de configuración no encontrado: {path}", path=config_path)
        raise typer.Exit(code=1)

    with open(config_file, "r", encoding="utf-8") as f:
        sources_config = yaml.safe_load(f)

    sources = sources_config.get("sources", [])
    documents = sources_config.get("documents", [])

    logger.info("Configuración cargada: {n_sources} fuentes, {n_docs} documentos", n_sources=len(sources), n_docs=len(documents))

    if dry_run:
        logger.info("MODO DRY-RUN: no se realizarán peticiones HTTP")
        for doc in documents:
            logger.info(
                "DRY-RUN: {doc_id} - {url} (tipo={tipo}, fecha={fecha})",
                doc_id=doc.get("id", "?"),
                url=doc.get("url", ""),
                tipo=doc.get("document_type", "?"),
                fecha=doc.get("date", "?"),
            )
        raise typer.Exit(code=0)

    # Construir componentes
    fetcher = Fetcher(
        user_agent=sources[0].get("user_agent", "VoxiTech Lab AI research") if sources else "VoxiTech Lab AI research",
        rate_limit_rps=sources[0].get("rate_limit_rps", 1.0) if sources else 1.0,
        respect_robots_txt=sources[0].get("respect_robots_txt", True) if sources else True,
    )
    downloader = Downloader(raw_root="data/raw")
    dedup_keys = ["url", "content_hash", "title_date_speaker"]
    dedup = DedupChecker(keys=dedup_keys, strategy="keep_first")
    registry = DocumentRegistry(db_path="data/processed/metadata.sqlite")

    ingester = Ingester(
        fetcher=fetcher,
        downloader=downloader,
        dedup=dedup,
        registry=registry,
    )

    results = ingester.ingest_sources_config(sources_config)

    successful = sum(1 for r in results if r["status"] == "ingested")
    skipped = sum(1 for r in results if r["status"] == "skipped_duplicate")
    failed = sum(1 for r in results if r["status"] == "failed")

    logger.info(
        "Ingesta completa: {ok} ingestados, {skip} omitidos (duplicados), {fail} fallidos",
        ok=successful,
        skip=skipped,
        fail=failed,
    )

    for r in results:
        if r["status"] == "failed":
            logger.error("FALLO: {url} - {reason}", url=r.get("url"), reason=r.get("reason"))


app = typer.Typer(help="Extracción de documentos de VoxiTech Lab AI")
app.command()(extract_command)


if __name__ == "__main__":
    app()