"""Order response models for API v2."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import field_validator

from ...enums import CreationStatus, OrderStatus, PaymentStatus
from .base import ResponseModel


class CreateOrderResponse(ResponseModel):
    """Response returned after an unpaid order is created."""

    custom_id: UUID
    total_to_pay: Decimal
    status: CreationStatus


class PaymentResponse(ResponseModel):
    """Immediate or asynchronous payment result."""

    custom_id: UUID
    status: PaymentStatus
    balance: Decimal
    pins: list[str] | None = None
    note: str | None = None


class OrderInfoResponse(ResponseModel):
    """Current state and delivered data for an order."""

    custom_id: UUID
    status: OrderStatus | int
    status_message: str
    product: str | None = None
    quantity: Decimal | None = None
    total_price: Decimal | None = None
    date: datetime
    pins: list[str] | None = None
    data: Any | None = None

    @field_validator("status", mode="before")
    @classmethod
    def parse_known_status(
        cls,
        value: object,
    ) -> OrderStatus | int:
        """Use enums for documented values and preserve future codes."""
        if isinstance(value, OrderStatus):
            return value
        if isinstance(value, bool) or not isinstance(value, (int, str)):
            raise ValueError("status must be an integer")
        numeric = int(value)
        try:
            return OrderStatus(numeric)
        except ValueError:
            return numeric
