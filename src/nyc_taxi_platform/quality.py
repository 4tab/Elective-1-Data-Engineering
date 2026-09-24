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