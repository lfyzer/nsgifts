"""Account response models."""

from decimal import Decimal

from .base import ResponseModel


class BalanceResponse(ResponseModel):
    """Current account balance in USD."""

    balance: Decimal
