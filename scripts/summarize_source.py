from __future__ import annotations
import sys
import duckdb
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw/yellow_tripdata_2025-01.parquet")
con = duckdb.connect()
print(con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [str(path)]).fetchdf().to_string(index=False))
print(con.execute("SELECT COUNT(*) AS rows FROM read_parquet(?)", [str(path)]).fetchdf().to_string(index=False))
