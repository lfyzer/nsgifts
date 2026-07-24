"""Steam-specific read and validation operations."""

from ..enums import APIOperation
from ..models import (
    ExchangeRateRequest,
    ExchangeRateResponse,
    SteamAppsResponse,
    SteamUserRequest,
    SteamUserResponse,
)
from .base import Transport


class SteamMethods:
    """Read Steam rates/apps and validate Steam accounts."""

    def __init__(self, transport: Transport) -> None:
        """Initialize the Steam method group."""
        self._transport = transport

    async def get_exchange_rate(
        self,
        service_id: int = 1,
    ) -> ExchangeRateResponse:
        """Return currency rates for a Steam top-up service."""
        request = ExchangeRateRequest(service_id=service_id)
        data = await self._transport.request(
            APIOperation.EXCHANGE_RATE,
            json_body=request.to_payload(),
        )
        return ExchangeRateResponse.model_validate(data)

    async def get_apps(self) -> SteamAppsResponse:
        """Return Steam applications available for gifts."""
        data = await self._transport.request(APIOperation.STEAM_GIFT_APPS)
        return SteamAppsResponse.model_validate(data)

    async def check_user(
        self,
        steam_id: str,
    ) -> SteamUserResponse:
        """Return whether a Steam account name exists."""
        request = SteamUserRequest(steam_id=steam_id)
        data = await self._transport.request(
            APIOperation.STEAM_CHECK_USER,
            json_body=request.to_payload(),
        )
        return SteamUserResponse.model_validate(data)
