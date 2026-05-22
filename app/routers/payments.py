from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Payment
from app.schemas.responses import (
    PaginatedResponse,
    PaginationMeta,
    PaymentResponse,
    RequestMeta,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=PaginatedResponse[PaymentResponse])
def get_payments(
    updated_after: datetime | None = Query(None, description="Extrae registros actualizados después de esta fecha (UTC)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Payment)

    if updated_after:
        query = query.filter(Payment.updated_at >= updated_after)

    total = query.count()

    payments = (
        query
        .order_by(Payment.updated_at)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        data=payments,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            has_next=(page * page_size) < total,
        ),
        metadata=RequestMeta(
            entity="payments",
            filter_field="updated_after",
            filter_value=str(updated_after) if updated_after else None,
            extracted_at=datetime.now(timezone.utc),
        ),
    )