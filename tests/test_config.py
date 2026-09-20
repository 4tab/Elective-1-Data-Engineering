from nyc_taxi_platform.config import Settings


def test_period_format() -> None:
    s = Settings(year=2025, month=1)
    assert s.period == "2025-01"
    assert s.raw_trip_file.name == "yellow_tripdata_2025-01.parquet"
