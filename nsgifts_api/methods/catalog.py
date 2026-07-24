"""Partner-specific stock catalog operations."""

from ..enums import APIOperation
from ..models import StockResponse
from .base import Transport


class CatalogMethods:
    """Read current categories, services, prices, and field schemas."""

    def __init__(self, transport: Transport) -> None:
        """Initialize the catalog method group."""
        self._transport = transport

    async def get_stock(self) -> StockResponse:
        """Return the live partner-specific stock catalog."""
        data = await self._transport.request(APIOperation.STOCK)
        return StockResponse.model_validate(data)
