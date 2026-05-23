install:
	poetry install

ingest:
	poetry run python -m ecobici_platform.ingestion.ecobici_batch

dbt-run:
	cd dbt && poetry run dbt run --profiles-dir .

feast-apply:
	cd feast_repo/feature_repo && poetry run feast apply

lint:
	poetry run ruff check src tests
	poetry run black --check src tests
