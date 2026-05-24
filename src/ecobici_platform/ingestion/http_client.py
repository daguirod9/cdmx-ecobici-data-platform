"""HTTP client implementation with retry semantics for unstable endpoints."""

from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from ecobici_platform.config.settings import settings
from ecobici_platform.ingestion.interfaces import ApiClient


class RequestsApiClient(ApiClient):
    """Simple reusable API client for JSON endpoints."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def fetch(self, endpoint: str) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/{endpoint.lstrip('/')}",
            timeout=settings.api_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()
