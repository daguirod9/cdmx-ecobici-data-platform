from pathlib import Path

from ecobici_platform.ingestion.ecobici_batch import (
    EcobiciBatchIngestionService,
    ensure_duckdb_parent_dir,
)


class DummyClient:
    def fetch(self, endpoint: str) -> dict:
        return {
            "last_updated": "2026-05-24T00:00:00Z",
            "endpoint": endpoint,
            "data": {"stations": []},
        }


class DummySink:
    def write(self, source_name: str, endpoint: str, payload: dict) -> str:
        return f"/tmp/{source_name}/{endpoint}.json"


def test_batch_ingestion_service_returns_records(monkeypatch) -> None:
    service = EcobiciBatchIngestionService()
    service.client = DummyClient()
    service.sink = DummySink()

    records = service.run(["station_status.json", "station_information.json"])

    assert len(records) == 2
    assert records[0].endpoint == "station_status.json"
    assert records[0].raw_path.endswith("station_status.json.json")
    assert records[1].endpoint == "station_information.json"


def test_ensure_duckdb_parent_dir_creates_missing_directory(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "ecobici.duckdb"

    ensure_duckdb_parent_dir(str(db_path))

    assert db_path.parent.exists()
