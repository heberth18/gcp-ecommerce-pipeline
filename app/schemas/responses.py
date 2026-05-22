from datetime import date, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    has_next: bool


class RequestMeta(BaseModel):
    entity: str
    filter_field: str
    filter_value: str | None
    extracted_at: datetime


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: PaginationMeta
    metadata: RequestMeta


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    email: str
    first_name: str        # may have leading/trailing spaces
    last_name: str
    country: str
    city: str | None       # null if not filled at registration
    registration_date: date
    created_at: datetime
    updated_at: datetime


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    name: str
    category: str          # mixed-case values
    description: str | None  # null if seller didn't provide one
    price: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    customer_id: str
    status: str            # occasionally uppercase
    total_amount: float
    created_at: datetime
    updated_at: datetime


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_item_id: str
    order_id: str
    product_id: str
    quantity: int
    unit_price: float
    subtotal: float
    created_at: datetime
    updated_at: datetime


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: str
    order_id: str
    payment_method: str | None  # null on system error
    status: str
    amount: str                 # DB stores Numeric; returned as string to simulate an API inconsistency
    created_at: datetime
    updated_at: datetime

    @field_validator("amount", mode="before")
    @classmethod
    def convert_amount_to_string(cls, v) -> str:
        # dbt staging layer resolves this with CAST(amount AS NUMERIC)
        return str(v)


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inventory_id: str
    product_id: str
    stock_quantity: int
    reorder_point: int
    last_restock_date: date | None  # null for newly added products
    created_at: datetime
    updated_at: datetime
