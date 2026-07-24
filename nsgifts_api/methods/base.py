"""Shared protocol for API method groups."""

from collections.abc import Mapping
from typing import Any, Protocol

from ..enums import APIOperation


class Transport(Protocol):
    """Transport behavior consumed by high-level method groups."""

    async def request(
        self,
        operation: APIOperation,
        *,
        json_body: Mapping[str, Any] | None = None,
        path_params: Mapping[str, Any] | None = None,
        query_params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send one validated API operation."""
