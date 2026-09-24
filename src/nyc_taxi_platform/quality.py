from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

import duckdb


@dataclass
class CheckResult:
    name: str
    passed: bool
    observed: object
    expectation: str
    severity: str = "ERROR"


def _table_exists(con: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    return bool(
        con.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
            [table_name],
        ).fetchone()[0]
    )