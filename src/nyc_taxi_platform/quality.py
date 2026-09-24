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


def run_quality_checks(con: duckdb.DuckDBPyConnection) -> list[CheckResult]:
    """Profile raw source data and gate the curated analytical dataset."""
    results: list[CheckResult] = []

    required = {
        "VendorID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "PULocationID",
        "DOLocationID",
        "payment_type",
        "total_amount",
    }
    cols = {row[0] for row in con.execute("DESCRIBE stage_trips").fetchall()}
    results.append(
        CheckResult(
            "required_columns",
            required.issubset(cols),
            sorted(cols),
            f"contains {sorted(required)}",
            "ERROR",
        )
    )


    # Public TLC data is vendor-submitted external data, so raw anomalies are
    # measured for observability rather than treated as automatic pipeline failure.

    raw_checks = [
        ("raw_null_pickup", "SELECT COUNT(*) FROM stage_trips WHERE tpep_pickup_datetime IS NULL", "0"),
        ("raw_null_dropoff", "SELECT COUNT(*) FROM stage_trips WHERE tpep_dropoff_datetime IS NULL", "0"),
        (
            "raw_bad_chronology",
            "SELECT COUNT(*) FROM stage_trips WHERE tpep_pickup_datetime >= tpep_dropoff_datetime",
            "0",
        ),
        ("raw_negative_distance", "SELECT COUNT(*) FROM stage_trips WHERE trip_distance < 0", "0"),
        (
            "raw_implausible_passengers",
            "SELECT COUNT(*) FROM stage_trips WHERE passenger_count < 0 OR passenger_count > 10",
            "0",
        ),
        (
            "raw_duplicate_trip_keys",
            "SELECT COUNT(*) FROM (SELECT trip_key FROM stage_trips GROUP BY trip_key HAVING COUNT(*) > 1)",
            "0",
        ),
        (
            "raw_unknown_pickup_zones",
            "SELECT COUNT(*) FROM stage_trips s LEFT JOIN zones z ON s.PULocationID = z.LocationID "
            "WHERE s.PULocationID IS NOT NULL AND z.LocationID IS NULL",
            "0",
        ),
        (
            "raw_unknown_dropoff_zones",
            "SELECT COUNT(*) FROM stage_trips s LEFT JOIN zones z ON s.DOLocationID = z.LocationID "
            "WHERE s.DOLocationID IS NOT NULL AND z.LocationID IS NULL",
            "0",
        ),
        (
            "raw_negative_total_amount",
            "SELECT COUNT(*) FROM stage_trips WHERE total_amount < 0",
            "0",
        ),
    ]
    for name, sql, expected in raw_checks:
        observed = con.execute(sql).fetchone()[0]
        results.append(CheckResult(name, observed == 0, observed, expected, "WARNING"))
    
    curated_exists = _table_exists(con, "curated_trips")
    results.append(
        CheckResult("curated_table_exists", curated_exists, curated_exists, "curated_trips exists", "ERROR")
    )

    if curated_exists:
        raw_count = con.execute("SELECT COUNT(*) FROM stage_trips").fetchone()[0]
        curated_count = con.execute("SELECT COUNT(*) FROM curated_trips").fetchone()[0]
        results.append(CheckResult("raw_row_count", True, raw_count, ">= 0", "INFO"))
        results.append(CheckResult("curated_row_count", curated_count > 0, curated_count, "> 0", "ERROR"))
        results.append(
            CheckResult("excluded_row_count", True, raw_count - curated_count, "reported for lineage", "INFO")
        )

        gate_checks = [
            ("curated_null_pickup", "SELECT COUNT(*) FROM curated_trips WHERE tpep_pickup_datetime IS NULL", "0"),
            ("curated_null_dropoff", "SELECT COUNT(*) FROM curated_trips WHERE tpep_dropoff_datetime IS NULL", "0"),
            (
                "curated_bad_chronology",
                "SELECT COUNT(*) FROM curated_trips WHERE tpep_pickup_datetime >= tpep_dropoff_datetime",
                "0",
            ),
            ("curated_negative_distance", "SELECT COUNT(*) FROM curated_trips WHERE trip_distance < 0", "0"),
            (
                "curated_implausible_passengers",
                "SELECT COUNT(*) FROM curated_trips WHERE passenger_count < 0 OR passenger_count > 10",
                "0",
            ),
            (
                "curated_duplicate_trip_keys",
                "SELECT COUNT(*) FROM (SELECT trip_key FROM curated_trips GROUP BY trip_key HAVING COUNT(*) > 1)",
                "0",
            ),
            (
                "curated_unknown_pickup_zones",
                "SELECT COUNT(*) FROM curated_trips s LEFT JOIN zones z ON s.PULocationID = z.LocationID "
                "WHERE z.LocationID IS NULL",
                "0",
            ),
            (
                "curated_unknown_dropoff_zones",
                "SELECT COUNT(*) FROM curated_trips s LEFT JOIN zones z ON s.DOLocationID = z.LocationID "
                "WHERE z.LocationID IS NULL",
                "0",
            ),
        ]
        for name, sql, expected in gate_checks:
            observed = con.execute(sql).fetchone()[0]
            results.append(CheckResult(name, observed == 0, observed, expected, "ERROR"))

    return results