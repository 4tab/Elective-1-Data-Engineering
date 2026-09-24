from __future__ import annotations

import logging
from pathlib import Path
from urllib.request import Request, urlopen

from .config import Settings

log = logging.getLogger(__name__)


def download_file(url: str, destination: Path, max_mb: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        log.info("Using existing file: %s", destination)
        return

    log.info("Downloading %s", url)
    request = Request(url, headers={"User-Agent": "nyc-taxi-data-platform/0.1"})
    with urlopen(request, timeout=60) as response, destination.open("wb") as out:
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > max_mb * 1024 * 1024:
            raise RuntimeError(f"Refusing file > {max_mb} MB: {url}")
        total = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_mb * 1024 * 1024:
                raise RuntimeError(f"Download exceeded {max_mb} MB: {url}")
            out.write(chunk)


def download_source(settings: Settings) -> None:
    trip_url = f"{settings.source_base_url}/trip-data/yellow_tripdata_{settings.period}.parquet"
    zone_url = f"{settings.source_base_url}/misc/taxi_zone_lookup.csv"
    download_file(trip_url, settings.raw_trip_file, settings.max_raw_file_mb)
    download_file(zone_url, settings.raw_zone_file, 10)