"""Tests for HMAC signing and replay protection."""

import base64
import hashlib
import hmac

import pytest

from nsgifts_api.auth import (
    HMACSigner,
    ReplayGuard,
    TokenState,
    request_fingerprint,
    serialize_json,
)
from nsgifts_api.errors import APIConfigurationError


def _expected_signature(
    secret: bytes,
    parts: list[str],
) -> str:
    """Calculate an independent expected HMAC signature."""
    value = "\n".join(parts).encode("utf-8")
    digest = hmac.new(secret, value, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("ascii")


def test_serialize_json_is_compact_and_preserves_unicode() -> None:
    """Verify that signed bytes are deterministic UTF-8 JSON."""
    body = serialize_json({"message": "Подарок", "quantity": 1})
    assert body == (
        b'{"message":"\xd0\x9f\xd0\xbe\xd0\xb4\xd0\xb0\xd1\x80\xd0\xbe\xd0\xba",'
        b'"quantity":1}'
    )


def test_serialize_none_produces_empty_body() -> None:
    """Verify hashing behavior for endpoints without a body."""
    assert serialize_json(None) == b""


def test_bootstrap_signature_omits_token_slot() -> None:
    """Verify the special get-token signing formula."""
    secret = b"secret-key"
    encoded_secret = base64.b64encode(secret).decode("ascii")
    body = serialize_json({"login": "partner", "password": "secret"})
    body_hash = hashlib.sha256(body).hexdigest()
    expected = _expected_signature(
        secret,
        [
            "POST",
            "/api/v2/get_token",
            "",
            "1720000000",
            body_hash,
        ],
    )

    result = HMACSigner(encoded_secret).sign(
        method="POST",
        path="/api/v2/get_token",
        query="",
        body=body,
        timestamp="1720000000",
        token=None,
    )

    assert result == expected


def test_authenticated_signature_contains_token_slot() -> None:
    """Verify the normal signing formula with a session token."""
    secret = b"secret-key"
    encoded_secret = base64.b64encode(secret).decode("ascii")
    body = b""
    expected = _expected_signature(
        secret,
        [
            "GET",
            "/api/v2/stock",
            "",
            "1720000000",
            "session-token",
            hashlib.sha256(body).hexdigest(),
        ],
    )

    result = HMACSigner(encoded_secret).sign(
        method="GET",
        path="/api/v2/stock",
        query="",
        body=body,
        timestamp="1720000000",
        token="session-token",
    )

    assert result == expected


def test_invalid_base64_secret_is_rejected_without_echo() -> None:
    """Verify fail-fast validation without revealing the value."""
    secret = "not valid base64!"
    with pytest.raises(APIConfigurationError) as error:
        HMACSigner(secret)
    assert secret not in str(error.value)


class FakeClock:
    """Controllable wall clock and sleeper for replay tests."""

    def __init__(self, value: float) -> None:
        """Initialize the fake timestamp."""
        self.value = value
        self.sleeps: list[float] = []

    def now(self) -> float:
        """Return the current fake timestamp."""
        return self.value

    async def sleep(self, delay: float) -> None:
        """Advance fake time instead of blocking."""
        self.sleeps.append(delay)
        self.value += delay


@pytest.mark.asyncio
async def test_replay_guard_delays_identical_request() -> None:
    """Verify unique timestamps for identical signatures."""
    clock = FakeClock(1720000000.1)
    guard = ReplayGuard(clock=clock.now, sleeper=clock.sleep)
    fingerprint = b"identical-request"

    first = await guard.timestamp_for(fingerprint)
    second = await guard.timestamp_for(fingerprint)

    assert first == "1720000000"
    assert second == "1720000001"
    assert clock.sleeps == pytest.approx([0.9])


@pytest.mark.asyncio
async def test_replay_guard_does_not_delay_different_requests() -> None:
    """Verify that different request signatures stay concurrent-safe."""
    clock = FakeClock(1720000000.1)
    guard = ReplayGuard(clock=clock.now, sleeper=clock.sleep)

    first = await guard.timestamp_for(b"request-one")
    second = await guard.timestamp_for(b"request-two")

    assert first == second == "1720000000"
    assert clock.sleeps == []


def test_request_fingerprint_changes_with_token_and_body() -> None:
    """Verify that all signature inputs affect replay identity."""
    first = request_fingerprint(
        "POST",
        "/api/v2/create_order",
        "",
        b'{"value":1}',
        "token-one",
    )
    second = request_fingerprint(
        "POST",
        "/api/v2/create_order",
        "",
        b'{"value":2}',
        "token-one",
    )
    third = request_fingerprint(
        "POST",
        "/api/v2/create_order",
        "",
        b'{"value":1}',
        "token-two",
    )
    assert len({first, second, third}) == 3


def test_token_state_masks_token_and_uses_monotonic_expiry() -> None:
    """Verify safe token storage and expiry calculations."""
    state = TokenState.issue(
        token="visible-token",
        expires_in=7200,
        clock=lambda: 100.0,
    )
    assert "visible-token" not in repr(state)
    assert state.value == "visible-token"
    assert not state.is_expiring(300, clock=lambda: 6999.0)
    assert state.is_expiring(300, clock=lambda: 7001.0)
