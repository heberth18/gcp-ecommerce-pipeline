
import io
import logging
import os
from datetime import date

import pandas as pd
from google.cloud import storage
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", "/opt/airflow/secrets/gcp-credentials.json")
BUCKET_NAME = os.getenv("GCS_BUCKET", "ecommerce-data-platform-raw")


def _get_client() -> storage.Client:
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return storage.Client(credentials=credentials)


def write_parquet_to_gcs(data: list[dict], entity: str, execution_date: str) -> str:
    df = pd.DataFrame(data)

    # convert timestamp strings to datetime so Parquet encodes them as INT64
    for col in ["created_at", "updated_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True).astype("datetime64[us, UTC]")

    df["execution_date"] = date.fromisoformat(execution_date)

    # convert date strings to date so Parquet encodes them as INT32
    for col in ["registration_date", "last_restock_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date

    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, compression="snappy")
    buffer.seek(0)

    path = f"raw/{entity}/ds={execution_date}/{entity}.parquet"
    client = _get_client()
    bucket = client.bucket(BUCKET_NAME)
    bucket.blob(path).upload_from_file(buffer, content_type="application/octet-stream")

    logger.info(f"Written {len(df)} rows to gs://{BUCKET_NAME}/{path}")
    return f"gs://{BUCKET_NAME}/{path}"