# Ecommerce Data Platform — GCP
![CI](https://github.com/heberth18/gcp-ecommerce-pipeline/actions/workflows/dbt_ci.yml/badge.svg)

Pipeline de Data Engineering end-to-end sobre GCP para un caso de uso real:
**startup e-commerce B2C que necesita métricas confiables, reproducibles y auditables de ventas y clientes.**

> Pipeline completo: simulador → Airflow → GCS → BigQuery → dbt → Looker Studio

---

## Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Airflow-017CEE?style=flat&logo=apacheairflow&logoColor=white)
![GCS](https://img.shields.io/badge/GCS-FBBC04?style=flat&logo=googlecloud&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-4285F4?style=flat&logo=googlebigquery&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=flat&logo=dbt&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

---

## Arquitectura

```
Python Ecommerce API Simulator (FastAPI + PostgreSQL)
    ↓  extracción incremental (updated_after)
Airflow DAG
    ↓  Parquet / Snappy
GCS — Storage Layer
    ↓  schema explícito · particionado por fecha
BigQuery Bronze — Raw Layer
    ↓  limpieza · normalización · tipado
dbt Staging
    ↓  modelado dimensional · KPIs
dbt Gold
    ↓
Looker Studio
```

---

## Highlights técnicos

- **Incremental extraction** con updated_after y estado persistente en Airflow Variables
- **Simulador realista** con 8 errores controlados para demostrar limpieza real en Staging
- **Stack completamente contenerizado** — un solo docker compose up levanta todo
- **Infraestructura como código** — GCS bucket y datasets de BigQuery provisionados con Terraform
- **CI/CD** — dbt test corre automáticamente en cada push via GitHub Actions
- **Idempotencia** en GCS y BigQuery — reejecutar el mismo run nunca duplica datos
- **Schema explícito** en BigQuery — cambios de tipo en la fuente fallan de forma visible
- **Arquitectura medallion** Bronze → Staging → Gold con separación estricta de responsabilidades
- **78 tests** de calidad de datos en Staging y Gold
- **Alertas en Airflow** — notificación por email si el DAG falla

## Modelado dimensional — dbt Gold

**Facts**
- `fct_orders` — una fila por orden con revenue real desde payments completados
- `fct_order_items` — una fila por ítem vendido con quantity, unit_price y subtotal

**Dimensions**
- `dim_customers` — atributos descriptivos de clientes
- `dim_products` — atributos descriptivos de productos

**KPIs pre-agregados**
- `kpi_revenue_by_month` — revenue y órdenes por mes
- `kpi_revenue_by_category` — revenue y unidades vendidas por categoría
- `kpi_orders_by_status` — conteo de órdenes por estado
- `kpi_revenue_by_country` — revenue y órdenes por país

---

## Dashboard

https://datastudio.google.com/reporting/73196a5d-33ff-4d5f-899a-07991cd8a774

---

## Correr el proyecto

```bash
cp .env.example .env
docker compose up --build

# Generar 6 meses de datos históricos
curl -X POST http://localhost:8000/generate

# Explorar la API del simulador
# http://localhost:8000/docs

# UI de Airflow
# http://localhost:8080
```

---

## Autor

**Heberth Caripa** · [LinkedIn](https://www.linkedin.com/in/heberth-caripa/)
