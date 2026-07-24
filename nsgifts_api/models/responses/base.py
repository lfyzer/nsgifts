"""Base response model helpers."""

from pydantic import BaseModel, ConfigDict


class ResponseModel(BaseModel):
    """Forward-compatible API response model."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
