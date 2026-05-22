import random
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.generator.factories import (
    make_customer,
    make_inventory,
    make_order,
    make_order_items,
    make_payment,
    make_product,
)

# --- Configuración de períodos ---
# Crecimiento progresivo: el negocio crece con el tiempo
# new_customers = customers NUEVOS en ese período (se acumulan)
PERIODS = [
    {"days_from": 180, "days_to": 120, "orders_per_day": 50,  "new_customers": 200},
    {"days_from": 120, "days_to":  60, "orders_per_day": 100, "new_customers": 300},
    {"days_from":  60, "days_to":   0, "orders_per_day": 200, "new_customers": 500},
]

PRODUCTS_TOTAL = 50
DUPLICATE_PAYMENT_RATE = 0.02  # error #5: 2% de órdenes tienen pago duplicado


def run(db: Session) -> dict:
    """
    Genera 6 meses de historia transaccional con coherencia temporal.
    Retorna un resumen de los registros creados.
    """
    today = date.today()
    summary = {
        "products": 0,
        "customers": 0,
        "orders": 0,
        "order_items": 0,
        "payments": 0,
        "duplicate_payments": 0,
    }

    # --- 1. Productos ---
    # Se generan todos al inicio: existían antes del período de análisis
    print("Generating products...")
    products = [make_product() for _ in range(PRODUCTS_TOTAL)]
    db.add_all(products)
    db.flush()
    summary["products"] = len(products)

    # --- 2. Inventario ---
    print("Generating inventory...")
    inventories = [make_inventory(p) for p in products]
    db.add_all(inventories)
    db.flush()

    # --- 3. Períodos ---
    all_customers = []  # los customers se acumulan entre períodos

    for i, period in enumerate(PERIODS, start=1):
        period_start = today - timedelta(days=period["days_from"])
        period_end = today - timedelta(days=period["days_to"])

        print(f"\nPeriod {i}: {period_start} → {period_end} "
            f"({period['orders_per_day']} orders/day, "
            f"{period['new_customers']} new customers)")

        # --- 4. Nuevos customers para este período ---
        new_customers = [
            make_customer(period_start, period_end)
            for _ in range(period["new_customers"])
        ]
        db.add_all(new_customers)
        db.flush()
        all_customers.extend(new_customers)
        summary["customers"] += len(new_customers)

        # --- 5. Órdenes día a día ---
        current_day = period_start
        while current_day < period_end:

            # varianza natural: ±20% alrededor del target diario
            n_orders = random.randint(
                int(period["orders_per_day"] * 0.8),
                int(period["orders_per_day"] * 1.2),
            )

            # solo customers registrados en o antes del día actual pueden comprar
            eligible = [
                c for c in all_customers
                if c.registration_date <= current_day
            ]

            if not eligible:
                current_day += timedelta(days=1)
                continue

            for _ in range(n_orders):
                customer = random.choice(eligible)

                # orden
                order = make_order(customer, current_day)
                db.add(order)
                db.flush()

                # items — determinan el total_amount de la orden
                items = make_order_items(order, products)
                db.add_all(items)

                order.total_amount = round(sum(item.subtotal for item in items), 2)
                db.flush()

                summary["orders"] += 1
                summary["order_items"] += len(items)

                # pago principal
                payment = make_payment(order)
                db.add(payment)
                summary["payments"] += 1

                # error #5: pago duplicado ocasional
                if random.random() < DUPLICATE_PAYMENT_RATE:
                    duplicate = make_payment(order)
                    db.add(duplicate)
                    summary["duplicate_payments"] += 1
                    summary["payments"] += 1

            db.commit()
            current_day += timedelta(days=1)

    print(f"\n✓ Generation complete: {summary}")
    return summary