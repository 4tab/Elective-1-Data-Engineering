"""Optional Airflow DAG. Install Airflow separately in an orchestrator environment."""

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="nyc_taxi_data_platform",
    start_date=datetime(2025, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["data-engineering", "elt", "quality"],
) as dag:
    download = BashOperator(
        task_id="download",
        bash_command="python -m nyc_taxi_platform.cli download",
    )
    run = BashOperator(
        task_id="run_pipeline",
        bash_command="python -m nyc_taxi_platform.cli run",
    )
    report = BashOperator(
        task_id="report",
        bash_command="python -m nyc_taxi_platform.cli report",
    )

    download >> run >> report
