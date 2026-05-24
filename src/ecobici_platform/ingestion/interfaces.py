"""Interfaces that keep ingestion reusable across APIs."""

from abc import ABC, abstractmethod
from typing import Any


class ApiClient(ABC):
    """Defines a fetch contract for any API source."""

    @abstractmethod
    def fetch(self, endpoint: str) -> dict[str, Any]:
        """Return normalized JSON payload for an endpoint."""


class PayloadSink(ABC):
    """Defines where and how raw payloads are persisted."""

    @abstractmethod
    def write(self, source_name: str, endpoint: str, payload: dict[str, Any]) -> str:
        """Persist payload and return its stored path."""
