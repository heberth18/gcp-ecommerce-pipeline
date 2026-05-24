from airflow.models import Variable
from datetime import timezone
import datetime

# Fallback timestamp for the initial full backfill
EPOCH_START = "1970-01-01T00:00:00+00:00"


def get_last_extracted(entity: str) -> str:
    """Return the last successful extraction timestamp for an entity, or EPOCH_START on first run."""
    key = f"{entity}_last_extracted"
    return Variable.get(key, default_var=EPOCH_START)


def set_last_extracted(entity: str, timestamp: str) -> None:
    """Persist the watermark for an entity after a successful extraction run."""
    key = f"{entity}_last_extracted"
    Variable.set(key, timestamp)


def get_run_timestamp() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.datetime.now(tz=timezone.utc).isoformat()
