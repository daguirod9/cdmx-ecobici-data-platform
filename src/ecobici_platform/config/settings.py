"""Centralized application settings for reproducible local and container execution."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PlatformSettings(BaseSettings):
    """Typed settings shared by ingestion, transformation, and feature workflows."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_base_url: str = Field(
        default="https://gbfs.mex.lyftbikes.com/gbfs/en",
        description="GBFS endpoint for Ecobici public feeds.",
    )
    api_timeout_seconds: int = 30
    raw_payload_root: str = "resources/raw_payloads"
    dlt_dataset_name: str = "ecobici_bronze"
    duckdb_path: str = "data/ecobici.duckdb"


settings = PlatformSettings()
