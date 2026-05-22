from datetime import date, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator

T = TypeVar("T")


# --- Wrappers de paginación ---

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


# --- Schemas por entidad ---
# Cada schema define exactamente qué devuelve el endpoint al DAG.
# Los errores realistas pasan sin modificación (espacios, nulos, mayúsculas).
# La excepción es payments.amount: se convierte de Numeric a str aquí.

class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    email: str
    first_name: str        # error #3: puede tener espacios extra
    last_name: str
    country: str
    city: str | None       # error #6: nulo si no completó el registro
    registration_date: date
    created_at: datetime
    updated_at: datetime


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    name: str
    category: str          # error #1: capitalización mezclada
    description: str | None  # error #6: nulo si el vendedor no lo completó
    price: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    customer_id: str
    status: str            # error #4: puede estar en mayúsculas
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
    payment_method: str | None  # error #8: nulo por error del sistema
    status: str
    amount: str                 # error #2: Numeric en DB → str en el endpoint
    created_at: datetime
    updated_at: datetime

    @field_validator("amount", mode="before")
    @classmethod
    def convert_amount_to_string(cls, v) -> str:
        """
        El amount se guarda como Numeric(10,2) en PostgreSQL.
        El endpoint lo devuelve como string para simular un error real de API.
        dbt Staging resolverá esto con CAST(amount AS NUMERIC).
        """
        return str(v)


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inventory_id: str
    product_id: str
    stock_quantity: int
    reorder_point: int
    last_restock_date: date | None  # error #7: nulo si producto nunca fue restockeado
    created_at: datetime
    updated_at: datetime