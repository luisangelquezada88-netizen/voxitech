"""Configuración de logging con Loguru."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def configure_logging(level: str = "INFO", log_file: str | Path | None = None) -> None:
    """Configura Loguru para el proyecto.

    Args:
        level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Ruta opcional a archivo de log. Si es None, solo se usa stderr.
    """
    logger.remove()

    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(sys.stderr, level=level, format=fmt, colorize=True)

    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_path,
            level=level,
            format=fmt,
            rotation="10 MB",
            retention="10 days",
            enqueue=True,
        )


def get_logger():
    """Retorna el logger configurado."""
    return logger