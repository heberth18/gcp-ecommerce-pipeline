import random
import uuid
from datetime import date, datetime, timedelta, timezone

from faker import Faker

from app.models.entities import Customer, Inventory, Order, OrderItem, Payment, Product

fake = Faker()

# --- Constants ---

# error #1: capitalización mezclada — vive en el endpoint, no aquí
# la DB guarda la categoría tal como está en esta lista
CATEGORIES = [
    "electronics", "Electronics", "ELECTRONICS",
    "clothing", "Clothing", "CLOTHING",
    "books", "Books", "BOOKS",
    "home", "Home", "HOME",
    "sports", "Sports", "SPORTS",
]

PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer"]

ORDER_STATUSES = ["pending", "confirmed", "shipped", "delivered", "cancelled", "returned"]


# --- Helpers ---

def _new_uuid() -> str:
    return str(uuid.uuid4())


def _random_datetime_on(day: date) -> datetime:
    """Genera un datetime aleatorio dentro de un día específico en UTC."""
    return datetime(
        day.year, day.month, day.day,
        random.randint(0, 23),
        random.randint(0, 59),
        random.randint(0, 59),
        tzinfo=timezone.utc,
    )


def _realistic_order_status(order_date: date) -> str:
    """
    Determina el status final de una orden según su antigüedad.
    Órdenes viejas están entregadas. Órdenes recientes están en tránsito.
    """
    age_days = (date.today() - order_date).days

    if age_days > 60:
        status = random.choices(
            ["delivered", "cancelled", "returned"],
            weights=[80, 15, 5],
        )[0]
    elif age_days > 30:
        status = random.choices(
            ["delivered", "shipped", "cancelled"],
            weights=[70, 20, 10],
        )[0]
    elif age_days > 7:
        status = random.choices(
            ["shipped", "confirmed", "delivered"],
            weights=[50, 30, 20],
        )[0]
    else:
        status = random.choices(
            ["pending", "confirmed", "shipped"],
            weights=[50, 35, 15],
        )[0]

    # error #4: 5% de las órdenes tienen status en mayúsculas
    if random.random() < 0.05:
        status = status.upper()

    return status


def _payment_status_for_order(order_status: str) -> str:
    """
    El status del pago debe ser coherente con el status de la orden.
    Una orden delivered casi siempre tiene pago completed.
    Una orden cancelled casi siempre tiene pago refunded o failed.
    """
    normalized = order_status.lower()  # maneja el error de mayúsculas

    if normalized in ["delivered", "shipped", "confirmed"]:
        return random.choices(["completed", "pending"], weights=[95, 5])[0]
    elif normalized in ["cancelled", "returned"]:
        return random.choices(["refunded", "failed"], weights=[70, 30])[0]
    else:
        return random.choices(["pending", "completed", "failed"], weights=[60, 30, 10])[0]


# --- Factories ---

def make_customer(period_start: date, period_end: date) -> Customer:
    registration_date = fake.date_between(start_date=period_start, end_date=period_end)
    created_at = _random_datetime_on(registration_date)

    first_name = fake.first_name()
    city = fake.city() if random.random() > 0.05 else None  # error #6: 5% nulo por dato faltante

    # error #3: 8% de first_name y city tienen espacios extra
    if random.random() < 0.08:
        first_name = f" {first_name} "
    if city and random.random() < 0.08:
        city = f" {city} "

    return Customer(
        customer_id=_new_uuid(),
        email=fake.unique.email(),
        first_name=first_name,
        last_name=fake.last_name(),
        country=fake.country(),
        city=city,
        registration_date=registration_date,
        created_at=created_at,
        updated_at=created_at,
    )


def make_product() -> Product:
    created_at = _random_datetime_on(
        date.today() - timedelta(days=random.randint(180, 365))
    )

    # error #1: capitalización mezclada — se guarda así en DB
    # el endpoint NO modifica esto, ya está inconsistente desde la fuente
    category = random.choice(CATEGORIES)

    # error #6: 15% de productos no tienen descripción
    description = fake.text(max_nb_chars=200) if random.random() > 0.15 else None

    return Product(
        product_id=_new_uuid(),
        name=fake.catch_phrase(),
        category=category,
        description=description,
        price=round(random.uniform(5.0, 999.99), 2),
        is_active=random.random() > 0.05,  # 5% inactivos
        created_at=created_at,
        updated_at=created_at,
    )


def make_inventory(product: Product) -> Inventory:
    # error #7: 10% de productos nunca fueron restockeados (productos nuevos)
    is_new_product = random.random() < 0.10

    return Inventory(
        inventory_id=_new_uuid(),
        product_id=product.product_id,
        stock_quantity=random.randint(0, 500),
        reorder_point=random.randint(10, 50),
        last_restock_date=None if is_new_product else fake.date_between(
            start_date=date.today() - timedelta(days=180),
            end_date=date.today(),
        ),
        created_at=product.created_at,
        updated_at=product.created_at,
    )


def make_order(customer: Customer, order_date: date) -> Order:
    created_at = _random_datetime_on(order_date)

    return Order(
        order_id=_new_uuid(),
        customer_id=customer.customer_id,
        status=_realistic_order_status(order_date),  # error #4 incluido
        total_amount=0,  # se actualiza después de crear los order_items
        created_at=created_at,
        updated_at=created_at,
    )


def make_order_items(order: Order, products: list[Product]) -> list[OrderItem]:
    active_products = [p for p in products if p.is_active]
    n_items = random.randint(1, 5)
    selected = random.sample(active_products, min(n_items, len(active_products)))

    items = []
    for product in selected:
        quantity = random.randint(1, 3)
        unit_price = float(product.price)  # precio inmutable al momento de la compra
        subtotal = round(quantity * unit_price, 2)

        items.append(OrderItem(
            order_item_id=_new_uuid(),
            order_id=order.order_id,
            product_id=product.product_id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
            created_at=order.created_at,
            updated_at=order.created_at,  # sin onupdate — append-only
        ))

    return items


def make_payment(order: Order) -> Payment:
    # error #8: 3% de pagos sin payment_method (error del sistema)
    payment_method = random.choice(PAYMENT_METHODS) if random.random() > 0.03 else None

    # el pago siempre ocurre después de la orden (entre 1 y 60 minutos después)
    payment_datetime = order.created_at + timedelta(minutes=random.randint(1, 60))

    return Payment(
        payment_id=_new_uuid(),
        order_id=order.order_id,
        payment_method=payment_method,
        status=_payment_status_for_order(order.status),
        amount=float(order.total_amount),  # Numeric en DB — string en endpoint (error #2)
        created_at=payment_datetime,
        updated_at=payment_datetime,
    )