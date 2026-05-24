from pathlib import Path

from ecobici_platform.ingestion.sinks import JsonFilePayloadSink


def test_json_file_payload_sink_writes_partitioned_payload(tmp_path: Path) -> None:
    sink = JsonFilePayloadSink(root_path=str(tmp_path))
    payload = {"last_updated": 123, "data": {"stations": []}}

    written_path = sink.write("sample_api", "station_status.json", payload)

    output = Path(written_path)
    assert output.exists()
    assert "sample_api" in output.parts
    assert "station_status" in output.parts
    assert output.read_text(encoding="utf-8")
