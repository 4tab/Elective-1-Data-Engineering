"""Optional Airflow DAG. Install Airflow separately in an orchestrator environment."""

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

