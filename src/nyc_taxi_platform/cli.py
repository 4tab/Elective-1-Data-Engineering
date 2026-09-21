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

@app.command()
def report() -> None:
    """Generate stakeholder/operations summaries from the warehouse."""
    pipeline().report()


@app.command()
def all() -> None:
    """Run the entire pipeline and generate operational outputs."""
    pipeline().all()


@app.command()
def clean() -> None:
    """Remove generated runtime data while keeping the repository structure."""
    for relative in ["data/raw", "data/staging", "data/curated", "data/warehouse", "data/quality", "reports"]:
        path = ROOT / relative
        path.mkdir(parents=True, exist_ok=True)
        for item in path.iterdir():
            if item.name == ".gitkeep":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    typer.echo("Generated runtime data removed.")