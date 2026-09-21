from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")



@dataclass(frozen=True)
class Settings:
    year: int = 2025
    month: int = 1
    max_raw_file_mb: int = 2048
    max_total_runtime_data_gb: int = 10
    source_base_url: str = "https://d37ci6vzurychx.cloudfront.net"
    warehouse_file: Path = ROOT / "data/warehouse/nyc_taxi.duckdb"

    @property
    def period(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"