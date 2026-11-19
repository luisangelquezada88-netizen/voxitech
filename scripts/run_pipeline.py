"""Punto de entrada reproducible para ejecutar el pipeline end-to-end."""

from __future__ import annotations

import typer
from voxitech.cli.pipeline import app as pipeline_app
from voxitech.cli.extract import app as extract_app

app = typer.Typer(help="VoxiTech Lab AI pipeline")
app.add_typer(pipeline_app, name="pipeline")
app.add_typer(extract_app, name="extract")


if __name__ == "__main__":
    app()