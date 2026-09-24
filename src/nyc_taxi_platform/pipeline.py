from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from .config import ROOT, Settings
from .download import download_source
from .quality import run_quality_checks, write_quality_report

log = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, settings: Settings) -> None:
        self.s = settings
        # Create every runtime directory up front so a fresh clone can run
        # successfully without requiring a prior `clean` command.
        for path in (
            self.s.raw_trip_file.parent,
            self.s.raw_zone_file.parent,
            self.s.curated_trip_file.parent,
            self.s.warehouse_file.parent,
            ROOT / "data/quality",
            ROOT / "reports",
        ):
            path.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.s.warehouse_file))

    def download(self) -> None:
        download_source(self.s)
