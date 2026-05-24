
import io
import pyarrow as pa
import pyarrow.parquet as pq
from google.cloud import storage


BUCKET_NAME = "ecommerce-data-platform-raw"


def write_parquet_to_gcs(records: list[dict], entity: str, execution_date: str) -> str:
    """
    Converts a list of dicts to Parquet/Snappy and uploads to GCS.
    Returns the GCS path of the written file.
    """
    if not records:
        return None

    # Convert to Arrow table and serialize as Parquet/Snappy in memory
    table = pa.Table.from_pylist(records)
    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="snappy")
    buffer.seek(0)

    # Build GCS path with Hive partitioning
    gcs_path = f"raw/{entity}/dt={execution_date}/{entity}.parquet"

    # Upload to GCS
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    blob.upload_from_file(buffer, content_type="application/octet-stream")

    return f"gs://{BUCKET_NAME}/{gcs_path}"