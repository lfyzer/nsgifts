"""Tests for the public NS.Gifts API v2 client facade."""

import asyncio
import base64
from typing import Any

import pytest

from nsgifts_api import ClientConfig, NSGiftsClient
from nsgifts_api.enums import APIOperation


def _config() -> ClientConfig:
    """Return deterministic client settings."""
    return ClientConfig(
        user_id=1234,
        login="partner",
        password="password",
        api_secret=base64.b64encode(b"secret").decode("ascii"),
    )


class FakeTransport:
    """Client-level transport double."""

    def __init__(self) -> None:
        """Initialize request and lifecycle counters."""
        self.requests: list[APIOperation] = []
        self.close_count = 0

    async def request(
        self,
        operation: APIOperation,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Return a token response after yielding control."""
        self.requests.append(operation)
        await asyncio.sleep(0)
        if operation is APIOperation.GET_TOKEN:
            return {
                "user_id": 1234,
                "token": "session-token",
                "expires_in": 7200,
            }
        raise AssertionError(f"Unexpected operation: {operation}")

    async def close(self) -> None:
        """Record transport closure."""
        self.close_count += 1


def test_client_exposes_only_v2_method_groups() -> None:
    """Verify the breaking v2 public surface."""
    client = NSGiftsClient(
        config=_config(),
        transport=FakeTransport(),
    )
    assert client.account is not None
    assert client.catalog is not None
    assert client.orders is not None
    assert client.steam is not None
    assert not hasattr(client, "user")
    assert not hasattr(client, "ip_whitelist")
    assert not hasattr(client, "services")


@pytest.mark.asyncio
async def test_concurrent_authentication_uses_one_request() -> None:
    """Verify lock-protected token bootstrap."""
    transport = FakeTransport()
    client = NSGiftsClient(
        config=_config(),
        transport=transport,
    )

    results = await asyncio.gather(
        client.authenticate(),
        client.authenticate(),
        client.authenticate(),
    )

    assert len(results) == 3
    assert transport.requests == [APIOperation.GET_TOKEN]
    assert all(
        result.token.get_secret_value() == "session-token" for result in results
    )


@pytest.mark.asyncio
async def test_token_provider_returns_masked_internal_state() -> None:
    """Verify lazy authentication for protected transport calls."""
    transport = FakeTransport()
    client = NSGiftsClient(
        config=_config(),
        transport=transport,
    )

    first = await client._provide_token(False)
    second = await client._provide_token(False)

    assert first == second == "session-token"
    assert transport.requests == [APIOperation.GET_TOKEN]


@pytest.mark.asyncio
async def test_concurrent_rejected_token_refresh_is_coalesced() -> None:
    """Refresh one rejected token only once across concurrent requests."""
    transport = FakeTransport()
    client = NSGiftsClient(
        config=_config(),
        transport=transport,
    )
    rejected_token = await client._provide_token(False, None)

    results = await asyncio.gather(
        client._provide_token(True, rejected_token),
        client._provide_token(True, rejected_token),
        client._provide_token(True, rejected_token),
    )

    assert results == ["session-token"] * 3
    assert transport.requests == [
        APIOperation.GET_TOKEN,
        APIOperation.GET_TOKEN,
    ]


@pytest.mark.asyncio
async def test_context_manager_closes_once() -> None:
    """Verify idempotent lifecycle cleanup."""
    transport = FakeTransport()
    client = NSGiftsClient(
        config=_config(),
        transport=transport,
    )

    async with client:
        await client.authenticate()
    await client.close()

    assert transport.close_count == 1
