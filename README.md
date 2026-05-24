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

## Local setup (dependencies and environment)

This section documents a reproducible setup to **run and test** the project locally.

### 1) System prerequisites

- **Python 3.11.x** (required by project constraints).
- **Poetry** (dependency and virtual environment management).
- **Git**.
- (Optional) **Docker and Docker Compose** for containerized execution.

Check installed versions:

```bash
python3 --version
poetry --version
git --version
docker --version
docker compose version
```

> Recommendation: use `pyenv` to pin Python 3.11 without affecting other projects.

### 2) Clone the repository

```bash
git clone <REPO_URL>
cd cdmx-ecobici-data-platform
```

### 3) Configure Python 3.11 for Poetry

If your system has multiple Python versions:

```bash
poetry env use python3.11
```

Confirm the selected interpreter:

```bash
poetry env info
```

### 4) Install project dependencies

Install all dependencies declared in `pyproject.toml`:

```bash
poetry install
```

If you need a clean reinstall (useful for conflict resolution):

```bash
poetry env remove --all
poetry env use python3.11
poetry install
```

### 5) Run a minimal installation check

```bash
poetry run python -c "import ecobici_platform; print('OK')"
poetry run pytest -q
```

If both commands pass, your local environment is ready.

## How to run the pipeline locally

### 1) Batch ingestion (API -> raw payloads / bronze)

```bash
poetry run python -m ecobici_platform.ingestion.ecobici_batch
```

### 2) dbt transformations (bronze -> silver -> gold)

```bash
cd dbt
poetry run dbt run --profiles-dir .
poetry run dbt test --profiles-dir .
cd ..
```

### 3) Apply Feast objects (feature repo)

```bash
cd feast_repo/feature_repo
poetry run feast apply
cd ../..
```

## Run tests locally

### Full test suite

```bash
poetry run pytest
```

### Quick test suite

```bash
poetry run pytest -q
```

### Ingestion-focused tests

```bash
poetry run pytest tests/test_ingestion_service.py -q
```

## Recommended local validation flow (before commit)

```bash
poetry run pytest -q
cd dbt && poetry run dbt test --profiles-dir . && cd ..
```

## Dependency troubleshooting

### Incompatible Python version error

Typical symptom: Poetry rejects installation because your Python version is outside the allowed range.

Solution:

1. Install Python 3.11.
2. Run `poetry env use python3.11`.
3. Reinstall dependencies with `poetry install`.

### Dependency resolution conflicts (stale lockfile or broken environment)

```bash
poetry env remove --all
poetry cache clear pypi --all
poetry install
```

### `dbt` or `feast` not found in the virtual environment

Make sure to invoke them with `poetry run`:

```bash
poetry run dbt --version
poetry run feast version
```

If they still fail, reinstall dependencies with `poetry install`.

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

## Target definition selected (implemented now)

We use a **proxy target** from consecutive station snapshots:

- `demand_departures_proxy = max(prev_bikes_available - bikes_available, 0)`
- `supply_arrivals_proxy = max(prev_docks_available - docks_available, 0)`
- `net_demand_pressure_proxy = demand_departures_proxy - supply_arrivals_proxy`

See `docs/target_definition.md` for assumptions and migration to real trips.

## Open questions for the next iteration

- Confirm serving SLA for online features (hourly, every 15 min, or sub-5-min).

## Dependency compatibility policy

To avoid resolver failures caused by transitive incompatibilities (especially around Feast/dlt stacks),
this project currently pins the runtime to **Python 3.11** (`>=3.11,<3.12`) and constrains
`tenacity` to `<9.0` and `pyarrow` to `<18.1` for `feast[duckdb]` (0.47.x) compatibility.

If you need Python 3.12+, first validate a full dependency upgrade matrix in CI before widening constraints.
