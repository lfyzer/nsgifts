"""Base request model helpers."""

from typing import Any, TypeAlias

from pydantic import BaseModel, ConfigDict

JSONScalar: TypeAlias = str | int | float | bool


class RequestModel(BaseModel):
    """Strict request model with JSON wire serialization."""

    model_config = ConfigDict(extra="forbid")

    def to_payload(self) -> dict[str, Any]:
        """Return a JSON-compatible request dictionary."""
        return self.model_dump(
            mode="json",
            by_alias=True,
            exclude_none=True,
        )
