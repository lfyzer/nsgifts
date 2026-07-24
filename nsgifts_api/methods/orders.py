"""Unified order creation, payment, and status operations."""

from collections.abc import Mapping, Sequence
from uuid import UUID, uuid4

from ..enums import APIOperation
from ..models import (
    CreateOrderRequest,
    CreateOrderResponse,
    JSONScalar,
    OrderField,
    OrderInfoResponse,
    OrderReference,
    PaymentResponse,
    PayOrderRequest,
)
from .base import Transport


class OrderMethods:
    """Create, pay, and inspect all API v2 order types."""

    def __init__(self, transport: Transport) -> None:
        """Initialize the order method group."""
        self._transport = transport

    async def create(
        self,
        *,
        service_id: int,
        fields: Sequence[OrderField | Mapping[str, JSONScalar]],
        custom_id: str | UUID | None = None,
    ) -> CreateOrderResponse:
        """Create an unpaid order using its dynamic field schema.

        Args:
            service_id: Current service ID from ``catalog.get_stock``.
            fields: Key/value pairs required by the category schema.
            custom_id: Optional UUID4 idempotency key.

        Returns:
            The created order and amount due.
        """
        normalized_fields = [
            field
            if isinstance(field, OrderField)
            else OrderField.model_validate(field)
            for field in fields
        ]
        request = CreateOrderRequest.model_validate(
            {
                "service_id": service_id,
                "custom_id": uuid4() if custom_id is None else custom_id,
                "fields": normalized_fields,
            }
        )
        data = await self._transport.request(
            APIOperation.CREATE_ORDER,
            json_body=request.to_payload(),
        )
        return CreateOrderResponse.model_validate(data)

    async def pay(
        self,
        custom_id: str | UUID,
        *,
        totp_code: str | None = None,
    ) -> PaymentResponse:
        """Pay a created order exactly once.

        Args:
            custom_id: UUID4 used to create the order.
            totp_code: Optional six-digit purchase-authenticator code.

        Returns:
            Immediate or asynchronous payment state.
        """
        request = PayOrderRequest.model_validate(
            {
                "custom_id": custom_id,
                "totp_code": totp_code,
            }
        )
        data = await self._transport.request(
            APIOperation.PAY_ORDER,
            json_body=request.to_payload(),
        )
        return PaymentResponse.model_validate(data)

    async def get(
        self,
        custom_id: str | UUID,
    ) -> OrderInfoResponse:
        """Return the current state and delivered order data."""
        request = OrderReference.model_validate({"custom_id": custom_id})
        value = str(request.custom_id)
        data = await self._transport.request(
            APIOperation.ORDER_INFO,
            path_params={"custom_id": value},
        )
        return OrderInfoResponse.model_validate(data)
