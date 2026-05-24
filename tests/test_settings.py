from ecobici_platform.config.settings import PlatformSettings


def test_settings_defaults() -> None:
    cfg = PlatformSettings()

    assert cfg.api_base_url.startswith("https://")
    assert cfg.raw_payload_root == "resources/raw_payloads"
    assert cfg.dlt_dataset_name == "ecobici_bronze"
