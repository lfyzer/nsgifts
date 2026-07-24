"""Steam request models for API v2."""

from pydantic import Field

from .base import RequestModel


class ExchangeRateRequest(RequestModel):
    """Request exchange rates for one service."""

    service_id: int = Field(default=1, gt=0)


class SteamUserRequest(RequestModel):
    """Request validation of a Steam account name."""

    steam_id: str = Field(
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_]{3,32}$",
    )
