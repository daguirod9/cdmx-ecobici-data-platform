"""Raw payload storage implementations."""

from datetime import UTC, datetime
from pathlib import Path
import json

from ecobici_platform.ingestion.interfaces import PayloadSink


class JsonFilePayloadSink(PayloadSink):
    """Store API payloads in a standard source/endpoint/date partition layout."""

    def __init__(self, root_path: str) -> None:
        self.root = Path(root_path)

    def write(self, source_name: str, endpoint: str, payload: dict) -> str:
        ts = datetime.now(UTC)
        partition = ts.strftime("%Y/%m/%d/%H")
        clean_endpoint = endpoint.replace("/", "_").replace(".json", "")
        target_dir = self.root / source_name / clean_endpoint / partition
        target_dir.mkdir(parents=True, exist_ok=True)

        file_path = target_dir / f"payload_{ts.strftime('%Y%m%dT%H%M%SZ')}.json"
        with file_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)

        return str(file_path)
