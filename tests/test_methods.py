"""Tests for high-level API v2 method groups."""

from collections.abc import Callable
from typing import Any

import pytest
from pydantic import ValidationError

from nsgifts_api.enums import APIOperation
from nsgifts_api.methods import (
    AccountMethods,
    CatalogMethods,
    OrderMethods,
    SteamMethods,
)
from nsgifts_api.models import OrderField

CUSTOM_ID = "a4cee2fe-ce8c-448b-bf2c-000000000001"


class FakeTransport:
    """Scripted transport for method model-boundary tests."""

    def __init__(
        self,
        outcomes: list[
            dict[str, Any]
            | Callable[
                [APIOperation, dict[str, Any]],
                dict[str, Any],
            ]
        ],
    ) -> None:
        """Initialize scripted outcomes."""
        self.outcomes = outcomes
        self.calls: list[tuple[APIOperation, dict[str, Any]]] = []

    async def request(
        self,
        operation: APIOperation,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Record a request and return its response."""
        self.calls.append((operation, kwargs))
        outcome = self.outcomes.pop(0)
        if callable(outcome):
            return outcome(operation, kwargs)
        return outcome


@pytest.mark.asyncio
async def test_account_and_catalog_methods_validate_responses() -> None:
    """Verify basic read-only method groups."""
    transport = FakeTransport(
        [
            {"balance": "100.2500"},
            {"categories": []},
        ]
    )

    balance = await AccountMethods(transport).get_balance()
    stock = await CatalogMethods(transport).get_stock()

    assert str(balance.balance) == "100.2500"
    assert stock.categories == []
    assert transport.calls[0][0] is APIOperation.CHECK_BALANCE
    assert transport.calls[1][0] is APIOperation.STOCK


@pytest.mark.asyncio
async def test_order_methods_build_v2_payloads() -> None:
    """Verify create, pay, and path-based order-info calls."""
    transport = FakeTransport(
        [
            {
                "custom_id": CUSTOM_ID,
                "total_to_pay": "2.0000",
                "status": "created",
            },
            {
                "custom_id": CUSTOM_ID,
                "status": "completed",
                "balance": "98.0000",
                "pins": [],
                "note": None,
            },
            {
                "custom_id": CUSTOM_ID,
                "status": 2,
                "status_message": "Completed",
                "date": "2026-05-04T22:55:36",
            },
        ]
    )
    methods = OrderMethods(transport)

    await methods.create(
        service_id=449,
        custom_id=CUSTOM_ID,
        fields=[OrderField(key="quantity", value=1)],
    )
    await methods.pay(CUSTOM_ID, totp_code="123456")
    await methods.get(CUSTOM_ID)

    create_kwargs = transport.calls[0][1]
    pay_kwargs = transport.calls[1][1]
    info_kwargs = transport.calls[2][1]
    assert create_kwargs["json_body"]["fields"] == [
        {"key": "quantity", "value": 1}
    ]
    assert pay_kwargs["json_body"]["totp_code"] == "123456"
    assert info_kwargs["path_params"] == {"custom_id": CUSTOM_ID}


@pytest.mark.asyncio
async def test_order_create_generates_uuid4() -> None:
    """Verify automatic idempotency-key generation."""

    def creation_response(
        operation: APIOperation,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        assert operation is APIOperation.CREATE_ORDER
        return {
            "custom_id": kwargs["json_body"]["custom_id"],
            "total_to_pay": "1.0000",
            "status": "created",
        }

    transport = FakeTransport([creation_response])
    result = await OrderMethods(transport).create(
        service_id=449,
        fields=[OrderField(key="quantity", value=1)],
    )
    assert result.custom_id.version == 4


@pytest.mark.asyncio
async def test_order_create_rejects_explicit_empty_custom_id() -> None:
    """Never replace an invalid explicit idempotency key."""
    transport = FakeTransport([])

    with pytest.raises(ValidationError):
        await OrderMethods(transport).create(
            service_id=449,
            custom_id="",
            fields=[OrderField(key="quantity", value=1)],
        )

    assert transport.calls == []


@pytest.mark.asyncio
async def test_steam_methods_use_unified_v2_operations() -> None:
    """Verify exchange-rate, apps, and account-check operations."""
    transport = FakeTransport(
        [
            {
                "service_id": 1,
                "date": "2026-05-04T22:55:00",
                "rates": {
                    "rub": 95.42,
                    "kzt": 480.10,
                    "uah": 41.30,
                },
            },
            {"apps": []},
            {"accountStatus": True},
        ]
    )
    methods = SteamMethods(transport)

    await methods.get_exchange_rate()
    await methods.get_apps()
    user = await methods.check_user("steam_login")

    assert user.account_status is True
    assert transport.calls[0][0] is APIOperation.EXCHANGE_RATE
    assert transport.calls[2][1]["json_body"] == {"steam_id": "steam_login"}
