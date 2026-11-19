"""Pipeline end-to-end: extracción, limpieza, segmentación, detección temática, codificación, análisis."""

from __future__ import annotations

import typer
from pathlib import Path

from voxitech.utils.logging import configure_logging, get_logger

logger = get_logger()


def run_pipeline(
    project: str = typer.Argument("trump_gender_2025_2026", help="ID del proyecto"),
    stages: str = typer.Option("extract", "--stages", "-s", help="Etapas separadas por comas: extract,clean,segment,detect,code,analyze,report"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Solo muestra qué se ejecutaría"),
) -> None:
    """Ejecuta el pipeline completo o por etapas para un proyecto dado."""
    configure_logging(level="INFO")

    stage_list = [s.strip() for s in stages.split(",") if s.strip()]
    logger.info("Proyecto: {project}", project=project)
    logger.info("Etapas: {stages}", stages=stage_list)

    if dry_run:
        logger.info("MODO DRY-RUN: no se ejecutarán transformaciones reales")
        for stage in stage_list:
            logger.info("DRY-RUN: ejecutaría etapa '{stage}'", stage=stage)
        raise typer.Exit(code=0)

    # Importar aquí para evitar dependencias pesadas si solo se quiere ver ayuda
    if "extract" in stage_list:
        from voxitech.cli.extract import extract_command

        extract_command(config_path=f"config/sources/white_house.yaml")

    if "clean" in stage_list:
        logger.warning("Etapa 'clean' aún no implementada (Fase 3)")

    if "segment" in stage_list:
        logger.warning("Etapa 'segment' aún no implementada (Fase 4)")

    if "detect" in stage_list:
        logger.warning("Etapa 'detect' aún no implementada (Fase 5)")

    if "code" in stage_list:
        logger.warning("Etapa 'code' aún no implementada (Fase 6)")

    if "analyze" in stage_list:
        logger.warning("Etapa 'analyze' aún no implementada (Fase 7)")

    if "report" in stage_list:
        logger.warning("Etapa 'report' aún no implementada (Fase 8)")

    logger.info("Pipeline finalizado para el proyecto {project}", project=project)


app = typer.Typer(help="Pipeline end-to-end de VoxiTech Lab AI")
app.command()(run_pipeline)


if __name__ == "__main__":
    app()