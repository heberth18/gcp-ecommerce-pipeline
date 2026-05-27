# Ecommerce Data Platform — GCP

Pipeline de Data Engineering end-to-end sobre GCP para un caso de uso real:
**startup e-commerce B2C que necesita métricas confiables, reproducibles y auditables de ventas y clientes.**

> 🚧 En desarrollo activo.

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

## Estado actual

| Componente | Estado |
|---|---|
| Simulador Ecommerce API (FastAPI + PostgreSQL) | ✅ Completado |
| Airflow DAG — extracción incremental | ✅ Completado |
| GCS — Parquet/Snappy particionado | ✅ Completado |
| BigQuery Bronze — schema explícito | ✅ Completado |
| dbt Staging | 🔄 En progreso |
| dbt Gold | ⏳ Pendiente |
| Looker Studio | ⏳ Pendiente |

---

## Highlights técnicos

- **Incremental extraction** con `updated_after` y estado persistente en Airflow Variables
- **Simulador realista** con 8 errores controlados para demostrar limpieza real en Staging
- **Stack completamente contenerizado** — un solo `docker compose up` levanta todo
- **Idempotencia** en GCS y BigQuery — reejecutar el mismo run nunca duplica datos
- **Schema explícito** en BigQuery — cambios de tipo en la fuente fallan de forma visible

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
