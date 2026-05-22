# Ecommerce Data Platform — GCP

Pipeline de Data Engineering end-to-end sobre GCP.

> 🚧 En construcción — siendo desarrollado activamente.

## Stack

`FastAPI` `PostgreSQL` `Airflow` `GCS` `BigQuery` `dbt` `Looker Studio` `Docker`

## Arquitectura

```
Simulador API (FastAPI + PostgreSQL)
    → Airflow DAG (extracción incremental)
    → GCS (Parquet/Snappy)
    → BigQuery Bronze → dbt Staging → dbt Gold
    → Looker Studio
```

## Estado actual

| Componente | Estado |
|---|---|
| Simulador Ecommerce API | ✅ Completado |
| Airflow DAG — extracción incremental | 🔄 En progreso |
| GCS, BigQuery Bronze | ⏳ Pendiente |
| dbt Staging + Gold | ⏳ Pendiente |
| Looker Studio | ⏳ Pendiente |

## Correr el simulador

```bash
cp .env.example .env
docker compose up --build
curl -X POST http://localhost:8000/generate
# http://localhost:8000/docs
```

## Autor

**Heberth Bermúdez** · [LinkedIn](https://linkedin.com/in/heberth18)