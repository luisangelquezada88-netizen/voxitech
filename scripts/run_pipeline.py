"""Punto de entrada reproducible para ejecutar el pipeline end-to-end."""

from __future__ import annotations

import typer

app = typer.Typer(help="VoxiTech Lab AI pipeline")


@app.command()
def extract(project: str = "trump_gender_2025_2026"):
    """Extrae discursos desde fuentes configurables."""
    typer.echo(f"Extracción para el proyecto: {project}")


@app.command()
def analyze(project: str = "trump_gender_2025_2026"):
    """Ejecuta análisis cuantitativo y genera figuras."""
    typer.echo(f"Análisis para el proyecto: {project}")


if __name__ == "__main__":
    app()