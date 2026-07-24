"""Steam response models for API v2."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import Field

from .base import ResponseModel


class ExchangeRates(ResponseModel):
    """Currency units required for one USD."""

    rub: Decimal
    kzt: Decimal
    uah: Decimal


class ExchangeRateResponse(ResponseModel):
    """Exchange rates for a service."""

    service_id: int
    date: datetime
    rates: ExchangeRates


class SteamApp(ResponseModel):
    """One Steam application and its dynamic package data."""

    app_id: int
    name: str
    data_json: dict[str, Any]


class SteamAppsResponse(ResponseModel):
    """Steam applications available for gifts."""

    apps: list[SteamApp]


class SteamUserResponse(ResponseModel):
    """Steam account validation result."""

    account_status: bool = Field(alias="accountStatus")
