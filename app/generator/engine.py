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

# Volumes increase over time to simulate business growth.
# new_customers is additive — customers accumulate across periods.
PERIODS = [
    {"days_from": 180, "days_to": 120, "orders_per_day": 50,  "new_customers": 200},
    {"days_from": 120, "days_to":  60, "orders_per_day": 100, "new_customers": 300},
    {"days_from":  60, "days_to":   0, "orders_per_day": 200, "new_customers": 500},
]

PRODUCTS_TOTAL = 50
DUPLICATE_PAYMENT_RATE = 0.02  # ~2% of orders get a duplicate payment


def run(db: Session) -> dict:
    """Seed 6 months of transactional history. Returns a record count summary."""
    today = date.today()
    summary = {
        "products": 0,
        "customers": 0,
        "orders": 0,
        "order_items": 0,
        "payments": 0,
        "duplicate_payments": 0,
    }

    print("Generating products...")
    products = [make_product() for _ in range(PRODUCTS_TOTAL)]
    db.add_all(products)
    db.flush()
    summary["products"] = len(products)

    print("Generating inventory...")
    inventories = [make_inventory(p) for p in products]
    db.add_all(inventories)
    db.flush()

    all_customers: list = []  # accumulates across periods

    for i, period in enumerate(PERIODS, start=1):
        period_start = today - timedelta(days=period["days_from"])
        period_end = today - timedelta(days=period["days_to"])

        print(f"\nPeriod {i}: {period_start} → {period_end} "
            f"({period['orders_per_day']} orders/day, "
            f"{period['new_customers']} new customers)")

        new_customers = [
            make_customer(period_start, period_end)
            for _ in range(period["new_customers"])
        ]
        db.add_all(new_customers)
        db.flush()
        all_customers.extend(new_customers)
        summary["customers"] += len(new_customers)

        current_day = period_start
        while current_day < period_end:

            # ±20% variance around the daily target
            n_orders = random.randint(
                int(period["orders_per_day"] * 0.8),
                int(period["orders_per_day"] * 1.2),
            )

            # only customers registered on or before today can place orders
            eligible = [
                c for c in all_customers
                if c.registration_date <= current_day
            ]

            if not eligible:
                current_day += timedelta(days=1)
                continue

            for _ in range(n_orders):
                customer = random.choice(eligible)

                order = make_order(customer, current_day)
                db.add(order)
                db.flush()

                items = make_order_items(order, products)
                db.add_all(items)

                order.total_amount = round(sum(item.subtotal for item in items), 2)
                db.flush()

                summary["orders"] += 1
                summary["order_items"] += len(items)

                payment = make_payment(order)
                db.add(payment)
                summary["payments"] += 1

                if random.random() < DUPLICATE_PAYMENT_RATE:
                    duplicate = make_payment(order)
                    db.add(duplicate)
                    summary["duplicate_payments"] += 1
                    summary["payments"] += 1

            db.commit()
            current_day += timedelta(days=1)

    print(f"\nGeneration complete: {summary}")
    return summary
