from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import entities  # noqa: F401 — register models with SQLAlchemy
from app.routers import customers, products, orders, order_items, payments, inventory

app = FastAPI(
    title="Ecommerce API Simulator",
    description="Simulates a production ecommerce API for the GCP Data Platform pipeline.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(order_items.router)
app.include_router(payments.router)
app.include_router(inventory.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/generate", summary="Seed 6 months of historical data into PostgreSQL")
def generate_data(db: Session = Depends(get_db)):
    """Populate the database with transactional history. Run once on an empty database."""
    from app.generator import engine as gen_engine
    summary = gen_engine.run(db)
    return {"status": "ok", "summary": summary}