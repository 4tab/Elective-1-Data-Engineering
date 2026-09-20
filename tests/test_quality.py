From pathlib import Path

import duckdb

from nyc_taxi_platform.quality import run_quality_checks, write_quality_report


def _make_conn() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("""
        CREATE TABLE zones(LocationID INTEGER, Borough VARCHAR, zone VARCHAR, service_zone VARCHAR)
    """)
    con.execute("INSERT INTO zones VALUES (1, 'Manhattan', 'Test Zone', 'Yellow Zone')")
    con.execute("""
        CREATE TABLE stage_trips(
            trip_key BIGINT,
            VendorID INTEGER,
            tpep_pickup_datetime TIMESTAMP,
            tpep_dropoff_datetime TIMESTAMP,
            passenger_count DOUBLE,
            trip_distance DOUBLE,
            PULocationID INTEGER,
            DOLocationID INTEGER,
            payment_type INTEGER,
            total_amount DOUBLE
        )
    """)
    con.execute("""
        INSERT INTO stage_trips VALUES
        (1, 1, '2025-01-01 09:00:00', '2025-01-01 09:20:00', 1, 3.2, 1, 1, 1, 22.5),
        (2, 2, '2025-01-01 10:00:00', '2025-01-01 10:10:00', 2, 1.4, 1, 1, 2, 12.0)
    """)
    con.execute("CREATE TABLE curated_trips AS SELECT * FROM stage_trips")
    return con
