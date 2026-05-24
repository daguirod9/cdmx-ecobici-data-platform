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

## Instalación local (dependencias y entorno)

Esta sección documenta una instalación reproducible para poder **ejecutar y probar** el proyecto localmente.

### 1) Prerrequisitos del sistema

- **Python 3.11.x** (requerido por las restricciones del proyecto).
- **Poetry** (gestión de dependencias y entorno virtual).
- **Git**.
- (Opcional) **Docker y Docker Compose** para ejecución en contenedores.

Verifica versiones:

```bash
python3 --version
poetry --version
git --version
docker --version
docker compose version
```

> Recomendación: usar `pyenv` para fijar Python 3.11 sin afectar otros proyectos.

### 2) Clonar el repositorio

```bash
git clone <URL_DEL_REPO>
cd cdmx-ecobici-data-platform
```

### 3) Configurar Python 3.11 para Poetry

Si tu sistema tiene múltiples versiones de Python:

```bash
poetry env use python3.11
```

Confirma el intérprete elegido:

```bash
poetry env info
```

### 4) Instalar dependencias del proyecto

Instala todas las dependencias declaradas en `pyproject.toml`:

```bash
poetry install
```

Si necesitas reinstalar desde cero (útil ante conflictos):

```bash
poetry env remove --all
poetry env use python3.11
poetry install
```

### 5) Verificar instalación mínima

```bash
poetry run python -c "import ecobici_platform; print('OK')"
poetry run pytest -q
```

Si ambos comandos pasan, el entorno local quedó listo.

## Cómo ejecutar el pipeline en local

### 1) Ingesta batch (API -> raw payloads / bronze)

```bash
poetry run python -m ecobici_platform.ingestion.ecobici_batch
```

### 2) Transformaciones dbt (bronze -> silver -> gold)

```bash
cd dbt
poetry run dbt run --profiles-dir .
poetry run dbt test --profiles-dir .
cd ..
```

### 3) Aplicar objetos de Feast (feature repo)

```bash
cd feast_repo/feature_repo
poetry run feast apply
cd ../..
```

## Ejecutar pruebas en local

### Suite completa

```bash
poetry run pytest
```

### Suite rápida

```bash
poetry run pytest -q
```

### Pruebas específicas de ingesta

```bash
poetry run pytest tests/test_ingestion_service.py -q
```

## Flujo recomendado de validación local (antes de commit)

```bash
poetry run pytest -q
cd dbt && poetry run dbt test --profiles-dir . && cd ..
```

## Troubleshooting de dependencias

### Error por versión de Python incompatible

Síntoma típico: Poetry rechaza instalación por rango de versión.

Solución:

1. Instalar Python 3.11.
2. Ejecutar `poetry env use python3.11`.
3. Reinstalar con `poetry install`.

### Conflictos de resolución (lock desactualizado o entorno dañado)

```bash
poetry env remove --all
poetry cache clear pypi --all
poetry install
```

### `dbt` o `feast` no encontrados dentro del entorno

Asegúrate de invocarlos con `poetry run`:

```bash
poetry run dbt --version
poetry run feast version
```

Si fallan, reinstala con `poetry install`.

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
