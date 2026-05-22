from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Order
from app.schemas.responses import (
    OrderResponse,
    PaginatedResponse,
    PaginationMeta,
    RequestMeta,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=PaginatedResponse[OrderResponse])
def get_orders(
    updated_after: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Order)

    if updated_after:
        query = query.filter(Order.updated_at >= updated_after)

    total = query.count()
    orders = (
        query
        .order_by(Order.updated_at)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        data=orders,
        pagination=PaginationMeta(page=page, page_size=page_size, total=total, has_next=(page * page_size) < total),
        metadata=RequestMeta(entity="orders", filter_field="updated_after", filter_value=str(updated_after) if updated_after else None, extracted_at=datetime.now(timezone.utc)),
    )