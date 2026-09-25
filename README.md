# NYC Taxi Data Platform — Production-Style Data Engineering Portfolio Project

A compact end-to-end data engineering project built around the **NYC TLC Yellow Taxi Trip Record** data. The project demonstrates the practical skills expected from an Associate Data Engineer and adds production-minded concerns: idempotent ingestion, layered storage, data quality gates, dimensional modeling, reusable Python modules, automated tests, SQL analytics, and operational reporting.

## What this demonstrates

- **SQL:** joins, aggregations, CTEs, window functions, constraints, dimensional/star schema design.
- **Python:** modular ETL code, configuration, logging, error handling, type hints, CLI execution, tests.
- **Data quality:** schema checks, null/range/duplicate checks, referential integrity, explicit quality thresholds.
- **Data formats:** CSV lookup + Parquet facts + SQL warehouse.
- **ETL/ELT:** extract raw Parquet, stage typed/validated data, build warehouse dimensions/facts, publish marts.
- **Scalability thinking:** DuckDB executes SQL directly over Parquet without requiring a large in-memory pandas load.
- **Orchestration:** an Airflow DAG is included as an optional orchestration layer.
- **DevOps:** reproducible setup scripts for Unix/WSL/Git Bash and Windows CMD, `.env` configuration, CI tests/linting.
- **Consulting mindset:** the project includes an operating contract, data dictionary, quality report, and stakeholder-ready SQL outputs.

## Architecture

```text
             NYC TLC public Parquet + zone CSV
                         |
                         v
                 [Extract / Ingest]
                         |
                         v
                  data/raw (Parquet)
                         |
              schema + quality gate
                         |
                         v
                data/staging (Parquet)
                         |
                         v
                    DuckDB
                 SQL warehouse
        +----------------+----------------+
        |                                 |
     dimensions                         fact_trips
        |                                 |
        +----------------+----------------+
                         |
                         v
                  analytics marts
                         |
             +-----------+-----------+
             |                       |
       SQL outputs             quality/ops report
```

## Data source

The default source is the **January 2025 NYC TLC Yellow Taxi Trip Record** plus the official taxi-zone lookup CSV. NYC TLC states that trip records are published monthly and stored in Parquet because of dataset size. The project deliberately downloads only one month to keep local storage comfortably below 10 GB.

Official source page: <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>

## Storage budget

The repository contains **no large source dataset**. the CLI `download` command downloads only the configured month on demand and enforces a configurable raw-file cap. Generated files can be removed with `python -m nyc_taxi_platform.cli clean`.

The default configuration targets approximately one monthly Parquet file plus a small lookup table. The project itself remains small in Git; downloaded source files stay outside version control.

## Quick start

### Linux / macOS / WSL / Git Bash

```bash
bash install.sh
source .venv/bin/activate
python -m nyc_taxi_platform.cli download
python -m nyc_taxi_platform.cli run
python -m nyc_taxi_platform.cli report
python -m pytest
```

### Windows CMD

```bat
install.bat
.venv\\Scripts\\activate
python -m nyc_taxi_platform.cli download
python -m nyc_taxi_platform.cli run
python -m nyc_taxi_platform.cli report
python -m pytest
```

PowerShell can run the same Python commands after activating the venv.

## One-command pipeline

After installation:

```bash
python -m nyc_taxi_platform.cli all
```

This performs:

1. download of source files when missing,
2. raw schema inspection,
3. staging transformation,
4. quality checks,
5. DuckDB warehouse build,
6. analytics marts,
7. JSON + Markdown operational report.

The pipeline is **idempotent**: re-running it replaces the generated period-specific staging/warehouse objects deterministically instead of duplicating records.

## Main tables

### Dimensions

- `dim_date`
- `dim_vendor`
- `dim_payment_type`
- `dim_rate_code`
- `dim_zone`

### Fact

- `fact_trip`

### Analytics marts

- `mart_daily_zone_performance`
- `mart_hourly_demand`
- `mart_payment_mix`

## Business questions answered

- How does trip demand vary by day and hour?
- Which pickup zones generate the most activity and revenue?
- What is the median/average trip distance by zone?
- How do payment methods differ by trip profile?
- Where are unusual trips concentrated after data-quality filtering?

## Production-minded details

### Data quality gate

The pipeline uses a two-layer quality approach:

- **Raw profiling:** nulls, bad chronology, negative distance, implausible passenger counts, duplicate keys, unknown zones, and negative totals are measured and written as warnings.
- **Curated gate:** records are filtered and deduplicated before the warehouse is built. Curated invariants are treated as errors, including empty output, invalid timestamps, negative distance, implausible passenger counts, duplicate keys, and unresolved zones.

This prevents a dirty external record from aborting an otherwise usable monthly load while still keeping the data-quality gate strict for trusted analytical outputs.

A quality report is written to `reports/quality_report.md` and `data/quality/quality_results.json`.

### Data contract

See `docs/data_contract.md`. It defines source assumptions, field types, quality rules, and ownership boundaries so a consultant can explain exactly what is guaranteed by the pipeline versus what is inherited from the source.

### SQL design

See `sql/01_schema.sql`, `sql/02_dimensions.sql`, `sql/03_fact.sql`, and `sql/04_marts.sql`. The design intentionally separates source/staging concerns from analytics-facing structures.

## Optional Airflow orchestration

`src/nyc_taxi_platform/airflow_dag.py` shows how the same CLI pipeline can be scheduled with Airflow. Airflow is kept **optional** because a full Airflow environment is unnecessarily heavy for local portfolio setup and is not natively supported as a simple Windows service.

For an interview, explain that the DAG delegates work to tested Python modules rather than hiding business logic inside operators.

## Testing

```bash
python -m pytest -q
```

Tests cover core transformations, key validation, SQL file presence, and quality-rule behavior.

## Linting

```bash
ruff check src tests scripts
```

## Portfolio / interview framing

A strong explanation is:

> "I built a production-minded ELT platform for NYC taxi data. I ingest Parquet and a reference CSV, profile source quality, curate and deduplicate the data behind a deterministic gate, model the trusted records as a star schema in DuckDB, publish analytics marts, and expose the workflow through a CLI and optional Airflow DAG. I kept the deployment footprint under 10 GB and separated source, staging, curated, warehouse, and mart layers."

## Repository map

```text
config/              pipeline settings
sql/                 warehouse schema + analytics SQL
src/nyc_taxi_platform/  reusable Python package
scripts/             bootstrap and utility scripts
data/                runtime data (ignored by git)
reports/             generated quality/ops reports
docs/                architecture + data contract
notebooks/           optional stakeholder walkthrough
.github/workflows/   CI
```

## Source notes

NYC TLC notes that the trip data are collected from technology providers and that TLC does not itself create the data or guarantee accuracy. This project therefore treats the source as an external dependency and adds local quality controls rather than assuming source perfection.


### First run troubleshooting

A fresh clone does not need a prior `clean` command. The pipeline creates its `data/raw`, `data/curated`, `data/warehouse`, `data/quality`, and `reports` directories automatically.

Run commands without copying the shell prompt symbol (for example, do not type `➜` from the terminal output).
