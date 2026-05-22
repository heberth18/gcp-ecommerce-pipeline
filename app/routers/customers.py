from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Customer
from app.schemas.responses import (
    CustomerResponse,
    PaginatedResponse,
    PaginationMeta,
    RequestMeta,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=PaginatedResponse[CustomerResponse])
def get_customers(
    updated_after: datetime | None = Query(None, description="Extrae registros actualizados después de esta fecha (UTC)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Customer)

    if updated_after:
        query = query.filter(Customer.updated_at >= updated_after)

    total = query.count()

    customers = (
        query
        .order_by(Customer.updated_at)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        data=customers,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            has_next=(page * page_size) < total,
        ),
        metadata=RequestMeta(
            entity="customers",
            filter_field="updated_after",
            filter_value=str(updated_after) if updated_after else None,
            extracted_at=datetime.now(timezone.utc),
        ),
    )