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

    def stage(self) -> None:
        if not self.s.raw_trip_file.exists() or not self.s.raw_zone_file.exists():
            raise FileNotFoundError("Raw source files missing. Run the download step first.")
        with self._connect() as con:
            con.execute("DROP TABLE IF EXISTS zones")
            con.execute("DROP TABLE IF EXISTS stage_trips")
            con.execute(
                "CREATE TABLE zones AS SELECT * FROM read_csv_auto(?, header=true)",
                [str(self.s.raw_zone_file)],
            )
            con.execute(
                """
                CREATE TABLE stage_trips AS
                SELECT
                    hash(
                        CAST(VendorID AS VARCHAR), '|',
                        CAST(tpep_pickup_datetime AS VARCHAR), '|',
                        CAST(tpep_dropoff_datetime AS VARCHAR), '|',
                        CAST(PULocationID AS VARCHAR), '|',
                        CAST(DOLocationID AS VARCHAR), '|',
                        CAST(total_amount AS VARCHAR)
                    ) AS trip_key,
                    CAST(VendorID AS INTEGER) AS VendorID,
                    CAST(tpep_pickup_datetime AS TIMESTAMP) AS tpep_pickup_datetime,
                    CAST(tpep_dropoff_datetime AS TIMESTAMP) AS tpep_dropoff_datetime,
                    CAST(passenger_count AS DOUBLE) AS passenger_count,
                    CAST(trip_distance AS DOUBLE) AS trip_distance,
                    CAST(RatecodeID AS INTEGER) AS RatecodeID,
                    CAST(store_and_fwd_flag AS VARCHAR) AS store_and_fwd_flag,
                    CAST(PULocationID AS INTEGER) AS PULocationID,
                    CAST(DOLocationID AS INTEGER) AS DOLocationID,
                    CAST(payment_type AS INTEGER) AS payment_type,
                    CAST(fare_amount AS DOUBLE) AS fare_amount,
                    CAST(extra AS DOUBLE) AS extra,
                    CAST(mta_tax AS DOUBLE) AS mta_tax,
                    CAST(tip_amount AS DOUBLE) AS tip_amount,
                    CAST(tolls_amount AS DOUBLE) AS tolls_amount,
                    CAST(improvement_surcharge AS DOUBLE) AS improvement_surcharge,
                    CAST(total_amount AS DOUBLE) AS total_amount,
                    CAST(congestion_surcharge AS DOUBLE) AS congestion_surcharge,
                    CAST(airport_fee AS DOUBLE) AS airport_fee,
                    CAST(cbd_congestion_fee AS DOUBLE) AS cbd_congestion_fee
                FROM read_parquet(?)
                """,
                [str(self.s.raw_trip_file)],
            )
            con.execute("DROP TABLE IF EXISTS curated_trips")
            con.execute(
                """
                CREATE TABLE curated_trips AS
                WITH ranked AS (
                    SELECT
                        s.*,
                        ROW_NUMBER() OVER (
                            PARTITION BY s.trip_key
                            ORDER BY s.tpep_pickup_datetime, s.tpep_dropoff_datetime
                        ) AS rn
                    FROM stage_trips s
                    JOIN zones p ON s.PULocationID = p.LocationID
                    JOIN zones d ON s.DOLocationID = d.LocationID
                    WHERE s.tpep_pickup_datetime IS NOT NULL
                      AND s.tpep_dropoff_datetime IS NOT NULL
                      AND s.tpep_pickup_datetime < s.tpep_dropoff_datetime
                      AND s.trip_distance >= 0
                      AND (s.passenger_count IS NULL OR s.passenger_count BETWEEN 0 AND 10)
                )
                SELECT * EXCLUDE (rn)
                FROM ranked
                WHERE rn = 1
                """
            )
            con.execute("COPY (SELECT * FROM curated_trips) TO ? (FORMAT PARQUET)", [str(self.s.curated_trip_file)])
        log.info("Staging complete for %s", self.s.period)
