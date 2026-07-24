"""Account operations."""

from ..enums import APIOperation
from ..models import BalanceResponse
from .base import Transport


class AccountMethods:
    """Read partner account information."""

    def __init__(self, transport: Transport) -> None:
        """Initialize the account method group."""
        self._transport = transport

    async def get_balance(self) -> BalanceResponse:
        """Return the current USD account balance."""
        data = await self._transport.request(APIOperation.CHECK_BALANCE)
        return BalanceResponse.model_validate(data)
