FROM python:3.11-slim

ENV POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1

RUN pip install "poetry==$POETRY_VERSION"
WORKDIR /app
COPY pyproject.toml README.md /app/
RUN poetry install --no-interaction --no-root
COPY . /app
RUN poetry install --no-interaction

CMD ["poetry", "run", "python", "-m", "ecobici_platform.ingestion.ecobici_batch"]
