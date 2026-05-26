
import logging
import os

from google.cloud import bigquery
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", "/opt/airflow/secrets/gcp-credentials.json")
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "ecommerce-data-platform-497218")
DATASET = "bronze"

# Partition column added by the pipeline — not a business field
_PARTITION_FIELD = bigquery.SchemaField("execution_date", "DATE")

SCHEMAS: dict[str, list[bigquery.SchemaField]] = {
    "customers": [
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("email", "STRING"),
        bigquery.SchemaField("first_name", "STRING"),
        bigquery.SchemaField("last_name", "STRING"),
        bigquery.SchemaField("country", "STRING"),
        bigquery.SchemaField("city", "STRING"),
        bigquery.SchemaField("registration_date", "DATE"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        _PARTITION_FIELD,
    ],
    "products": [
        bigquery.SchemaField("product_id", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("category", "STRING"),
        bigquery.SchemaField("price", "FLOAT64"),
        bigquery.SchemaField("is_active", "BOOLEAN"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        _PARTITION_FIELD,
    ],
    "orders": [
        bigquery.SchemaField("order_id", "STRING"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("total_amount", "FLOAT64"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        _PARTITION_FIELD,
    ],
    "order_items": [
        bigquery.SchemaField("order_item_id", "STRING"),
        bigquery.SchemaField("order_id", "STRING"),
        bigquery.SchemaField("product_id", "STRING"),
        bigquery.SchemaField("quantity", "INTEGER"),
        bigquery.SchemaField("unit_price", "FLOAT64"),
        bigquery.SchemaField("subtotal", "FLOAT64"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        _PARTITION_FIELD,
    ],
    "payments": [
        bigquery.SchemaField("payment_id", "STRING"),
        bigquery.SchemaField("order_id", "STRING"),
        bigquery.SchemaField("payment_method", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("amount", "STRING"),  # arrives as string from API — fixed in Staging
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        _PARTITION_FIELD,
    ],
    "inventory": [
        bigquery.SchemaField("inventory_id", "STRING"),
        bigquery.SchemaField("product_id", "STRING"),
        bigquery.SchemaField("stock_quantity", "INTEGER"),
        bigquery.SchemaField("reorder_point", "INTEGER"),
        bigquery.SchemaField("last_restock_date", "DATE"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        _PARTITION_FIELD,
    ],
}


def _get_client() -> bigquery.Client:
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return bigquery.Client(project=PROJECT_ID, credentials=credentials)


def load_parquet_to_bronze(gcs_uri: str, entity: str, execution_date: str) -> dict:
    """Load a Parquet file from GCS into a partitioned Bronze table.

    Uses WRITE_TRUNCATE on the specific date partition — reruns overwrite
    only that day, historical partitions are never touched.
    """
    client = _get_client()

    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET}")
    dataset_ref.location = "US"
    client.create_dataset(dataset_ref, exists_ok=True)

    # partition decorator: overwrites only this date's slice
    partition_id = execution_date.replace("-", "")  # "2025-01-01" → "20250101"
    destination = f"{PROJECT_ID}.{DATASET}.{entity}${partition_id}"

    job_config = bigquery.LoadJobConfig(
        schema=SCHEMAS[entity],
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="execution_date",
        ),
    )

    logger.info(f"Loading {gcs_uri} → {destination}")
    load_job = client.load_table_from_uri(gcs_uri, destination, job_config=job_config)
    load_job.result()

    table = client.get_table(f"{PROJECT_ID}.{DATASET}.{entity}")
    logger.info(f"{entity}: {load_job.output_rows} rows loaded, {table.num_rows} total")

    return {"entity": entity, "rows_loaded": load_job.output_rows, "total_rows": table.num_rows}