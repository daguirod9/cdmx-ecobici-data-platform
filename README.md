# CDMX Ecobici Data Platform

End-to-end modular data platform for **hourly/day-of-week demand and availability prediction** on Ecobici stations in CDMX.

## Architecture

This repository implements a **Medallion architecture** with an incremental path from batch to micro-batch ingestion:

- **Raw zone (API payload archive):** immutable JSON payloads partitioned by source/endpoint/hour.
- **Bronze (DuckDB via dlt):** minimally structured records from raw feed.
- **Silver (dbt):** cleaned, typed, analytics-ready station status snapshots.
- **Gold (dbt star schema):** dimensions and facts for forecasting features.
- **Feature Store (Feast):** offline/online feature definitions for ML training and serving.

## Why this design scales

- Current ingestion runs in batch but uses reusable contracts (`ApiClient`, `PayloadSink`) to onboard new APIs quickly.
- Partitioned raw payloads preserve lineage and enable replay for micro-batch backfills.
- dlt resource pattern can shift from scheduled batch to frequent micro-batch runs without redesigning schemas.
- dbt transformations and Feast definitions are decoupled, so model feature iteration is independent of ingestion changes.

## Design patterns used

- **Strategy pattern (lightweight):** interchangeable implementations for `ApiClient` and `PayloadSink`.
- **Service layer:** `EcobiciBatchIngestionService` orchestrates domain flow without leaking I/O details.
- **Data contract through typed settings:** `PlatformSettings` centralizes runtime configuration for reproducibility.

## Project structure

- `src/ecobici_platform/ingestion`: reusable ingestion module.
- `resources/raw_payloads`: partitioned API payload storage.
- `dbt/`: medallion SQL models and Gold star schema.
- `feast_repo/feature_repo`: Feast registry and feature views.
- `notebooks/`: feature-engineering exploration notebooks.

## Quickstart

```bash
poetry install
poetry run python -m ecobici_platform.ingestion.ecobici_batch
cd dbt && poetry run dbt run --profiles-dir .
cd ../feast_repo/feature_repo && poetry run feast apply
```

## Gold layer star schema

### Dimensions
- `dim_time`: calendar attributes for day-level analysis.
- `dim_hour`: hourly demand windows.

### Facts
- `fact_station_availability`: station snapshot grain at `(station_id, status_timestamp)` with bike/dock metrics.

### Mart
- `mart_hourly_demand_proxy`: aggregate view for baseline demand behavior by hour/day-window.

## Next step to micro-batches

1. Trigger ingestion every 5-15 minutes via scheduler (Prefect/Airflow/Cron).
2. Add watermark state (last fetched timestamp) and idempotent merge strategy in bronze.
3. Incremental dbt models for silver/gold.
4. Feast materialization jobs at aligned windows.

## Open questions for the next iteration

- Confirm canonical target variable for demand forecasting (e.g., trips proxy vs stock depletion proxy).
- Confirm serving SLA for online features (hourly, every 15 min, or sub-5-min).
