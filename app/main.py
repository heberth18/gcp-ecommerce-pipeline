from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import entities  # noqa: F401 — importar para que SQLAlchemy registre los modelos
from app.routers import customers, products, orders, order_items, payments, inventory

app = FastAPI(
    title="Ecommerce API Simulator",
    description="Simulates a production ecommerce API for the GCP Data Platform pipeline.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

# --- Routers ---
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(order_items.router)
app.include_router(payments.router)
app.include_router(inventory.router)


# --- Endpoints de utilidad ---

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/generate", summary="Genera 6 meses de datos históricos en PostgreSQL")
def generate_data(db: Session = Depends(get_db)):
    """
    Pobla la base de datos con 6 meses de historia transaccional.
    Incluye los 8 errores realistas definidos en el diseño.
    Solo debe ejecutarse una vez sobre una base de datos vacía.
    """
    from app.generator import engine as gen_engine
    summary = gen_engine.run(db)
    return {"status": "ok", "summary": summary}