"""Batch ingestion entrypoint with a design that can evolve to micro-batches."""

from collections.abc import Iterable
from dataclasses import dataclass

import dlt

from ecobici_platform.config.settings import settings
from ecobici_platform.ingestion.http_client import RequestsApiClient
from ecobici_platform.ingestion.sinks import JsonFilePayloadSink


@dataclass
class IngestionRecord:
    endpoint: str
    ingested_at: str
    raw_path: str
    payload: dict


class EcobiciBatchIngestionService:
    """Coordinates endpoint extraction and storage into raw zone plus bronze loading."""

    def __init__(self) -> None:
        self.client = RequestsApiClient(base_url=settings.api_base_url)
        self.sink = JsonFilePayloadSink(root_path=settings.raw_payload_root)

    def run(self, endpoints: Iterable[str]) -> list[IngestionRecord]:
        output: list[IngestionRecord] = []
        for endpoint in endpoints:
            payload = self.client.fetch(endpoint)
            raw_path = self.sink.write(
                source_name="ecobici_gbfs", endpoint=endpoint, payload=payload
            )
            output.append(
                IngestionRecord(
                    endpoint=endpoint,
                    ingested_at=payload.get("last_updated", ""),
                    raw_path=raw_path,
                    payload=payload,
                )
            )
        return output


@dlt.resource(name="station_status_raw", write_disposition="append")
def station_status_resource(records: list[IngestionRecord]):
    for record in records:
        if record.endpoint.endswith("station_status.json"):
            yield {
                "endpoint": record.endpoint,
                "raw_path": record.raw_path,
                "last_updated": record.payload.get("last_updated"),
                "ttl": record.payload.get("ttl"),
                "stations": record.payload.get("data", {}).get("stations", []),
            }


def run_batch_pipeline() -> None:
    service = EcobiciBatchIngestionService()
    records = service.run(["station_information.json", "station_status.json"])

    pipeline = dlt.pipeline(
        pipeline_name="ecobici_batch_pipeline",
        destination=dlt.destinations.duckdb(settings.duckdb_path),
        dataset_name=settings.dlt_dataset_name,
    )
    pipeline.run(station_status_resource(records=records))


if __name__ == "__main__":
    run_batch_pipeline()
