import logging
from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from utils.api_client import fetch_entity
from utils.state_manager import get_last_extracted, set_last_extracted, get_run_timestamp
from utils.gcs_writer import write_parquet_to_gcs
from utils.bq_loader import load_parquet_to_bronze

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


def get_run_ts(**context) -> None:
    ts = get_run_timestamp()
    logger.info(f"Run timestamp: {ts}")
    context["ti"].xcom_push(key="run_timestamp", value=ts)


def extract_entity(entity: str, **context) -> None:
    run_timestamp = context["ti"].xcom_pull(
        task_ids="get_run_timestamp", key="run_timestamp"
    )
    since = get_last_extracted(entity)
    execution_date = context["ds"]

    logger.info(f"[{entity}] Extracting since: {since}")
    logger.info(f"[{entity}] Run timestamp: {run_timestamp}")

    all_records = []
    for page_records in fetch_entity(entity=entity, since_timestamp=since):
        all_records.extend(page_records)

    logger.info(f"[{entity}] Total records extracted: {len(all_records)}")

    gcs_path = write_parquet_to_gcs(
        data=all_records,
        entity=entity,
        execution_date=execution_date,
    )
    logger.info(f"[{entity}] Written to GCS: {gcs_path}")

    context["ti"].xcom_push(key=f"{entity}_gcs_path", value=gcs_path)

    set_last_extracted(entity, run_timestamp)
    logger.info(f"[{entity}] Watermark updated to: {run_timestamp}")


def load_to_bronze(entity: str, **context) -> dict:
    # pulls the GCS path pushed by the extract task for this entity
    gcs_uri = context["ti"].xcom_pull(
        task_ids=f"extract_{entity}",
        key=f"{entity}_gcs_path",
    )
    return load_parquet_to_bronze(
        gcs_uri=gcs_uri,
        entity=entity,
        execution_date=context["ds"],
    )


with DAG(
    dag_id="ecommerce_extraction",
    description="Incremental extraction from the FastAPI simulator to GCS",
    schedule_interval="@daily",
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

    load_tasks = []  # accumulates load tasks to connect with dbt_run later

    for entity in ENTITIES:
        extract_task = PythonOperator(
            task_id=f"extract_{entity}",
            python_callable=extract_entity,
            op_kwargs={"entity": entity},
        )

        load_task = PythonOperator(
            task_id=f"load_{entity}_bq",
            python_callable=load_to_bronze,
            op_kwargs={"entity": entity},
        )

        load_tasks.append(load_task)

        get_timestamp_task >> extract_task >> load_task

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "dbt run "
            "--project-dir /opt/airflow/dbt "
            "--profiles-dir /opt/airflow/dbt"
        ),
    )

    load_tasks >> dbt_run