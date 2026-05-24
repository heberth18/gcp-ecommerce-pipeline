import os
import requests
import logging
from typing import Generator

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://localhost:8000")

# order_items is append-only, so it uses created_after instead of updated_after
APPEND_ONLY_ENTITIES = {"order_items"}


def fetch_entity(
    entity: str,
    since_timestamp: str,
    page_size: int = 100,
) -> Generator[list[dict], None, None]:
    """Yield pages of records for a given entity, paginating until exhausted."""
    filter_param = (
        "created_after" if entity in APPEND_ONLY_ENTITIES else "updated_after"
    )

    page = 1
    total_fetched = 0

    while True:
        params = {
            filter_param: since_timestamp,
            "page": page,
            "page_size": page_size,
        }

        url = f"{BASE_URL}/{entity}"
        logger.info(f"[{entity}] GET {url} — page {page}, since {since_timestamp}")

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        records = data.get("data", [])

        if not records:
            logger.info(f"[{entity}] No more records. Total fetched: {total_fetched}")
            break

        total_fetched += len(records)
        logger.info(f"[{entity}] Page {page}: {len(records)} records")

        yield records

        if len(records) < page_size:
            logger.info(f"[{entity}] Last page reached. Total: {total_fetched}")
            break

        page += 1