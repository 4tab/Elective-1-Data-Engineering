from __future__ import annotations

import shutil
from pathlib import Path

import typer

from .config import ROOT, load_settings
from .logging_utils import configure_logging
from .pipeline import Pipeline

app = typer.Typer(add_completion=False)


def pipeline() -> Pipeline:
    configure_logging()
    return Pipeline(load_settings())


@app.command()
def download() -> None:
    """Download the configured monthly source files."""
    pipeline().download()


@app.command()
def run() -> None:
    """Run download, staging, quality gate, and warehouse build."""
    pipeline().run()

