from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from .config import ROOT, Settings
from .download import download_source
from .quality import run_quality_checks, write_quality_report

log = logging.getLogger(__name__)