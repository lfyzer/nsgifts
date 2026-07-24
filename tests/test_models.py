"""Tests for typed API v2 request and response models."""

from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError

from nsgifts_api.enums import (
    OrderStatus,
    PaymentStatus,
    StockFieldType,
)
from nsgifts_api.models import (
    CreateOrderRequest,
    CreateOrderResponse,
    OrderField,
    OrderInfoResponse,
    PaymentResponse,
    PayOrderRequest,
    SteamUserResponse,
    StockResponse,
    TokenRequest,
)

CUSTOM_ID = "a4cee2fe-ce8c-448b-bf2c-000000000001"


def test_token_request_masks_password_but_serializes_wire_value() -> None:
    """Verify secret masking and explicit wire serialization."""
    request = TokenRequest(login="partner", password="visible-secret")
    assert "visible-secret" not in repr(request)
    assert request.to_payload() == {
        "login": "partner",
        "password": "visible-secret",
    }


def test_create_order_request_uses_uuid4_and_dynamic_fields() -> None:
    """Verify the common v2 order structure."""
    request = CreateOrderRequest(
        service_id=449,
        custom_id=CUSTOM_ID,
        fields=[OrderField(key="quantity", value=2)],
    )
    payload = request.to_payload()
    assert payload["custom_id"] == CUSTOM_ID
    assert payload["fields"] == [{"key": "quantity", "value": 2}]


def test_create_order_rejects_non_uuid4_custom_id() -> None:
    """Verify strict idempotency-key validation."""
    with pytest.raises(ValidationError):
        CreateOrderRequest(
            service_id=449,
            custom_id="not-a-uuid",
            fields=[OrderField(key="quantity", value=1)],
        )


def test_pay_order_masks_and_validates_totp() -> None:
    """Verify six-digit TOTP handling."""
    request = PayOrderRequest(
        custom_id=CUSTOM_ID,
        totp_code="123456",
    )
    assert "123456" not in repr(request)
    assert request.to_payload()["totp_code"] == "123456"
    with pytest.raises(ValidationError):
        PayOrderRequest(
            custom_id=CUSTOM_ID,
            totp_code="12345x",
        )


def test_stock_response_uses_decimal_and_preserves_extensions() -> None:
    """Verify stock types and forward-compatible response fields."""
    response = StockResponse.model_validate(
        {
            "categories": [
                {
                    "category_name": "Gift Cards",
                    "category_id": 17,
                    "services": [
                        {
                            "service_id": 20,
                            "service_name": "Card",
                            "price": 1.928,
                            "currency": "USD",
                            "in_stock": 73,
                        }
                    ],
                    "fields": [
                        {
                            "key": "quantity",
                            "type": "int",
                            "name": "Quantity",
                            "required": True,
                            "min": 1,
                            "max": 100,
                            "step": 1,
                        }
                    ],
                    "future_category_value": "kept",
                }
            ],
            "future_root_value": "kept",
        }
    )
    category = response.categories[0]
    assert category.services[0].price == Decimal("1.928")
    assert category.fields[0].type is StockFieldType.INTEGER
    assert category.model_extra == {"future_category_value": "kept"}
    assert response.model_extra == {"future_root_value": "kept"}


def test_order_responses_use_uuid_decimal_and_enums() -> None:
    """Verify creation, payment, and order-info response types."""
    created = CreateOrderResponse.model_validate(
        {
            "custom_id": CUSTOM_ID,
            "total_to_pay": "3.8560",
            "status": "created",
        }
    )
    payment = PaymentResponse.model_validate(
        {
            "custom_id": CUSTOM_ID,
            "status": "completed",
            "balance": "127.4153",
            "pins": ["PIN-CODE"],
            "note": None,
        }
    )
    info = OrderInfoResponse.model_validate(
        {
            "custom_id": CUSTOM_ID,
            "status": 2,
            "status_message": "Completed",
            "product": "Gift Card",
            "quantity": 2.0,
            "total_price": 3.856,
            "date": "2026-05-04T22:55:36",
            "pins": ["PIN-CODE"],
            "data": None,
        }
    )

    assert isinstance(created.custom_id, UUID)
    assert created.total_to_pay == Decimal("3.8560")
    assert payment.status is PaymentStatus.COMPLETED
    assert payment.balance == Decimal("127.4153")
    assert info.status is OrderStatus.COMPLETED
    assert info.total_price == Decimal("3.856")


def test_order_info_preserves_future_status_codes() -> None:
    """Preserve unknown numeric statuses and reject invalid status types."""
    payload = {
        "custom_id": CUSTOM_ID,
        "status": 999,
        "status_message": "Future status",
        "date": "2026-05-04T22:55:36",
    }
    response = OrderInfoResponse.model_validate(payload)
    assert response.status == 999

    with pytest.raises(ValidationError):
        OrderInfoResponse.model_validate({**payload, "status": []})


def test_alias_response_is_pythonic_and_round_trippable() -> None:
    """Verify server aliases remain available on the wire."""
    response = SteamUserResponse.model_validate({"accountStatus": True})
    assert response.account_status is True
    assert response.model_dump(by_alias=True) == {"accountStatus": True}
