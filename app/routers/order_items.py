from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import OrderItem
from app.schemas.responses import (
    OrderItemResponse,
    PaginatedResponse,
    PaginationMeta,
    RequestMeta,
)

router = APIRouter(prefix="/order_items", tags=["order_items"])


@router.get("", response_model=PaginatedResponse[OrderItemResponse])
def get_order_items(
    # order_items es append-only: nunca se modifica, solo se crea
    # por eso usa created_after en lugar de updated_after
    created_after: datetime | None = Query(None, description="Extrae registros creados después de esta fecha (UTC)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(OrderItem)

    if created_after:
        query = query.filter(OrderItem.created_at >= created_after)

    total = query.count()

    items = (
        query
        .order_by(OrderItem.created_at)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            has_next=(page * page_size) < total,
        ),
        metadata=RequestMeta(
            entity="order_items",
            filter_field="created_after",  # distinto al resto — append-only
            filter_value=str(created_after) if created_after else None,
            extracted_at=datetime.now(timezone.utc),
        ),
    )