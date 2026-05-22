from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Product
from app.schemas.responses import (
    PaginatedResponse,
    PaginationMeta,
    ProductResponse,
    RequestMeta,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=PaginatedResponse[ProductResponse])
def get_products(
    updated_after: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Product)

    if updated_after:
        query = query.filter(Product.updated_at >= updated_after)

    total = query.count()
    products = (
        query
        .order_by(Product.updated_at)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        data=products,
        pagination=PaginationMeta(page=page, page_size=page_size, total=total, has_next=(page * page_size) < total),
        metadata=RequestMeta(entity="products", filter_field="updated_after", filter_value=str(updated_after) if updated_after else None, extracted_at=datetime.now(timezone.utc)),
    )