import json
import logging
from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.operators.python import PythonOperator

from utils.api_client import fetch_entity
from utils.state_manager import get_last_extracted, set_last_extracted, get_run_timestamp
from utils.gcs_writer import write_parquet_to_gcs

logger = logging.getLogger(__name__)

ENTITIES = [
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "inventory",
]

default_args = {
    "owner": "data_engineering",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def extract_entity(entity: str, **context) -> None:
    """Extract all new records for an entity and write them to GCS as Parquet/Snappy."""
    run_timestamp = context["ti"].xcom_pull(
        task_ids="get_run_timestamp", key="run_timestamp"
    )
    since = get_last_extracted(entity)
    execution_date = context["ds"]  # YYYY-MM-DD — used for GCS partition

    logger.info(f"[{entity}] Extracting since: {since}")
    logger.info(f"[{entity}] Run timestamp: {run_timestamp}")

    all_records = []
    for page_records in fetch_entity(entity=entity, since_timestamp=since):
        all_records.extend(page_records)

    logger.info(f"[{entity}] Total records extracted: {len(all_records)}")

    # Write to GCS — XCom carries only the file path, not the data
    gcs_path = write_parquet_to_gcs(
        records=all_records,
        entity=entity,
        execution_date=execution_date,
    )
    logger.info(f"[{entity}] Written to GCS: {gcs_path}")

    context["ti"].xcom_push(key=f"{entity}_gcs_path", value=gcs_path)

    # Only advance the watermark if extraction succeeded
    set_last_extracted(entity, run_timestamp)
    logger.info(f"[{entity}] Watermark updated to: {run_timestamp}")


def get_run_ts(**context) -> None:
    """Capture a single cut-off timestamp shared by all entity tasks in this run."""
    ts = get_run_timestamp()
    logger.info(f"Run timestamp: {ts}")
    context["ti"].xcom_push(key="run_timestamp", value=ts)


with DAG(
    dag_id="ecommerce_extraction",
    description="Incremental extraction from the FastAPI simulator to GCS",
    schedule_interval="@hourly",
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["ecommerce", "extraction", "bronze"],
) as dag:

    get_timestamp_task = PythonOperator(
        task_id="get_run_timestamp",
        python_callable=get_run_ts,
    )

    extraction_tasks = []
    for entity in ENTITIES:
        task = PythonOperator(
            task_id=f"extract_{entity}",
            python_callable=extract_entity,
            op_kwargs={"entity": entity},
        )
        extraction_tasks.append(task)

    get_timestamp_task >> extraction_tasks