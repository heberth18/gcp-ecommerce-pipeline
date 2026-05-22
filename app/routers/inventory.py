from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Inventory
from app.schemas.responses import (
    InventoryResponse,
    PaginatedResponse,
    PaginationMeta,
    RequestMeta,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=PaginatedResponse[InventoryResponse])
def get_inventory(
    updated_after: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Inventory)

    if updated_after:
        query = query.filter(Inventory.updated_at >= updated_after)

    total = query.count()
    inventory = (
        query
        .order_by(Inventory.updated_at)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        data=inventory,
        pagination=PaginationMeta(page=page, page_size=page_size, total=total, has_next=(page * page_size) < total),
        metadata=RequestMeta(entity="inventory", filter_field="updated_after", filter_value=str(updated_after) if updated_after else None, extracted_at=datetime.now(timezone.utc)),
    )