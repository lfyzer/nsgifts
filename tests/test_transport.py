"""Tests for the signed asynchronous HTTP transport."""

import asyncio
import base64
import json
from collections.abc import Callable
from typing import Any

import aiohttp
import pytest

from nsgifts_api.auth import HMACSigner, ReplayGuard
from nsgifts_api.config import ClientConfig
from nsgifts_api.enums import APIOperation
from nsgifts_api.errors import (
    APIAuthenticationError,
    APIClockSkewError,
    APIConflictError,
    APIForbiddenError,
    APIRequestOutcomeUnknownError,
    APITotpRequiredError,
)
from nsgifts_api.transport import SignedTransport


class FakeResponse:
    """Minimal aiohttp response double."""

    def __init__(
        self,
        status: int,
        payload: Any,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Store response status, payload, and headers."""
        self.status = status
        self.payload = payload
        self.headers = headers or {}

    async def read(self) -> bytes:
        """Return a JSON or text response body."""
        if isinstance(self.payload, BaseException):
            raise self.payload
        if isinstance(self.payload, bytes):
            return self.payload
        if isinstance(self.payload, str):
            return self.payload.encode("utf-8")
        return json.dumps(self.payload).encode("utf-8")


class FakeRequestContext:
    """Asynchronous request context double."""

    def __init__(
        self,
        outcome: FakeResponse | BaseException,
    ) -> None:
        """Store the response or exception to yield."""
        self.outcome = outcome

    async def __aenter__(self) -> FakeResponse:
        """Yield the response or raise the network exception."""
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        """Leave the fake context."""


class FakeSession:
    """Scripted aiohttp session double."""

    def __init__(
        self,
        outcomes: list[FakeResponse | BaseException],
    ) -> None:
        """Initialize scripted request outcomes."""
        self.outcomes = outcomes
        self.calls: list[dict[str, Any]] = []
        self.closed = False

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> FakeRequestContext:
        """Record a request and return its scripted outcome."""
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self.outcomes:
            raise AssertionError("No scripted response remains")
        return FakeRequestContext(self.outcomes.pop(0))

    async def close(self) -> None:
        """Mark the session as closed."""
        self.closed = True


class FakeClock:
    """Shared deterministic clock and sleeper."""

    def __init__(self, value: float = 1720000000.1) -> None:
        """Initialize deterministic time."""
        self.value = value
        self.sleeps: list[float] = []

    def now(self) -> float:
        """Return current time."""
        return self.value

    async def sleep(self, delay: float) -> None:
        """Record and advance sleep time."""
        self.sleeps.append(delay)
        self.value += delay


class FakeTokenProvider:
    """Record normal and forced token requests."""

    def __init__(self) -> None:
        """Initialize token-provider state."""
        self.calls: list[bool] = []
        self.rejected_tokens: list[str | None] = []
        self.token = "session-token"

    async def __call__(
        self,
        force_refresh: bool,
        rejected_token: str | None,
    ) -> str:
        """Return a deterministic session token."""
        self.calls.append(force_refresh)
        self.rejected_tokens.append(rejected_token)
        if force_refresh:
            self.token = "refreshed-token"
        return self.token


def _config(**overrides: Any) -> ClientConfig:
    """Create a valid transport configuration."""
    values: dict[str, Any] = {
        "user_id": 1234,
        "login": "partner",
        "password": "password",
        "api_secret": base64.b64encode(b"transport-secret").decode("ascii"),
        "max_retries": 2,
    }
    values.update(overrides)
    return ClientConfig(**values)


def _transport(
    outcomes: list[FakeResponse | BaseException],
    *,
    config: ClientConfig | None = None,
    token_provider: Callable[[bool], Any] | None = None,
) -> tuple[
    SignedTransport,
    FakeSession,
    FakeClock,
    FakeTokenProvider,
]:
    """Create a fully deterministic signed transport."""
    actual_config = config or _config()
    session = FakeSession(outcomes)
    clock = FakeClock()
    provider = token_provider or FakeTokenProvider()
    transport = SignedTransport(
        config=actual_config,
        signer=HMACSigner(actual_config.api_secret),
        token_provider=provider,
        session=session,
        replay_guard=ReplayGuard(
            clock=clock.now,
            sleeper=clock.sleep,
        ),
        sleeper=clock.sleep,
        random_source=lambda: 0.0,
    )
    return transport, session, clock, provider


@pytest.mark.asyncio
async def test_signed_request_sends_exact_serialized_bytes() -> None:
    """Verify that transmitted bytes are the bytes that were signed."""
    transport, session, _, provider = _transport(
        [FakeResponse(200, {"accountStatus": True})]
    )

    result = await transport.request(
        APIOperation.STEAM_CHECK_USER,
        json_body={"steam_id": "partner"},
    )

    call = session.calls[0]
    assert result == {"accountStatus": True}
    assert call["method"] == "POST"
    assert call["url"].endswith("/api/v2/steam/check_user")
    assert call["data"] == b'{"steam_id":"partner"}'
    assert call["headers"]["X-Timestamp"] == "1720000000"
    assert call["headers"]["X-Token"] == "session-token"
    assert call["headers"]["X-Signature"]
    assert call["allow_redirects"] is False
    assert provider.calls == [False]


@pytest.mark.asyncio
async def test_safe_get_retries_connection_failure() -> None:
    """Verify safe operations retry with a new signature."""
    transport, session, clock, _ = _transport(
        [
            aiohttp.ClientConnectionError("temporary"),
            FakeResponse(200, {"balance": "10.0000"}),
        ]
    )

    result = await transport.request(APIOperation.CHECK_BALANCE)

    assert result == {"balance": "10.0000"}
    assert len(session.calls) == 2
    assert clock.sleeps
    assert (
        session.calls[0]["headers"]["X-Signature"]
        != session.calls[1]["headers"]["X-Signature"]
    )


@pytest.mark.asyncio
async def test_unsafe_timeout_is_not_retried() -> None:
    """Verify payment uncertainty never triggers a duplicate call."""
    transport, session, _, _ = _transport([asyncio.TimeoutError()])

    with pytest.raises(APIRequestOutcomeUnknownError) as error:
        await transport.request(
            APIOperation.PAY_ORDER,
            json_body={"custom_id": ("a4cee2fe-ce8c-448b-bf2c-000000000001")},
        )

    assert len(session.calls) == 1
    assert error.value.custom_id == ("a4cee2fe-ce8c-448b-bf2c-000000000001")


@pytest.mark.asyncio
async def test_unsafe_truncated_response_has_unknown_outcome() -> None:
    """Treat response-stream failure after payment as an unknown outcome."""
    transport, session, _, _ = _transport(
        [FakeResponse(200, aiohttp.ClientPayloadError("truncated"))]
    )

    with pytest.raises(APIRequestOutcomeUnknownError):
        await transport.request(
            APIOperation.PAY_ORDER,
            json_body={"custom_id": "a4cee2fe-ce8c-448b-bf2c-000000000001"},
        )

    assert len(session.calls) == 1


@pytest.mark.asyncio
async def test_safe_operation_retries_truncated_response() -> None:
    """Retry a safe operation after a response-stream failure."""
    transport, session, _, _ = _transport(
        [
            FakeResponse(200, aiohttp.ClientPayloadError("truncated")),
            FakeResponse(200, {"balance": "10.0000"}),
        ]
    )

    result = await transport.request(APIOperation.CHECK_BALANCE)

    assert result == {"balance": "10.0000"}
    assert len(session.calls) == 2


@pytest.mark.asyncio
async def test_protected_401_refreshes_token_once() -> None:
    """Verify one forced refresh and one newly signed request."""
    transport, session, _, provider = _transport(
        [
            FakeResponse(401, {"detail": "Expired token"}),
            FakeResponse(200, {"categories": []}),
        ]
    )

    result = await transport.request(APIOperation.STOCK)

    assert result == {"categories": []}
    assert provider.calls == [False, True]
    assert session.calls[0]["headers"]["X-Token"] == ("session-token")
    assert session.calls[1]["headers"]["X-Token"] == ("refreshed-token")


@pytest.mark.asyncio
async def test_bootstrap_401_retries_once_with_new_timestamp() -> None:
    """Verify bounded recovery from cross-process replay collision."""
    transport, session, _, provider = _transport(
        [
            FakeResponse(401, {"detail": "Replay detected"}),
            FakeResponse(
                200,
                {
                    "user_id": 1234,
                    "token": "new-token",
                    "expires_in": 7200,
                },
            ),
        ]
    )

    result = await transport.request(
        APIOperation.GET_TOKEN,
        json_body={"login": "partner", "password": "password"},
    )

    assert result["token"] == "new-token"
    assert provider.calls == []
    assert len(session.calls) == 2
    assert "X-Token" not in session.calls[0]["headers"]
    assert (
        session.calls[0]["headers"]["X-Timestamp"]
        != session.calls[1]["headers"]["X-Timestamp"]
    )


@pytest.mark.asyncio
async def test_bootstrap_bad_credentials_are_not_retried() -> None:
    """Do not resend credentials for an ordinary authentication failure."""
    transport, session, _, provider = _transport(
        [FakeResponse(401, {"detail": "Invalid credentials"})]
    )

    with pytest.raises(APIAuthenticationError):
        await transport.request(
            APIOperation.GET_TOKEN,
            json_body={"login": "partner", "password": "wrong"},
        )

    assert len(session.calls) == 1
    assert provider.calls == []


@pytest.mark.asyncio
async def test_specialized_protected_401_is_not_refreshed() -> None:
    """Do not hide clock or signature failures behind token refresh."""
    clock_transport, clock_session, _, clock_provider = _transport(
        [FakeResponse(401, {"detail": "Timestamp outside allowed window"})]
    )
    with pytest.raises(APIClockSkewError):
        await clock_transport.request(APIOperation.STOCK)
    assert len(clock_session.calls) == 1
    assert clock_provider.calls == [False]

    signature_transport, signature_session, _, signature_provider = _transport(
        [FakeResponse(401, {"detail": "Invalid signature"})]
    )
    with pytest.raises(APIAuthenticationError):
        await signature_transport.request(APIOperation.STOCK)
    assert len(signature_session.calls) == 1
    assert signature_provider.calls == [False]


@pytest.mark.asyncio
async def test_transport_redacts_current_token_from_server_error() -> None:
    """Do not expose the signed token when a server response echoes it."""
    transport, _, _, _ = _transport(
        [
            FakeResponse(
                403,
                {
                    "detail": "Forbidden session-token",
                    "access_token": "session-token",
                },
            )
        ]
    )

    with pytest.raises(APIForbiddenError) as error:
        await transport.request(APIOperation.STOCK)

    assert "session-token" not in str(error.value)


@pytest.mark.asyncio
async def test_conflict_and_totp_errors_are_not_retried() -> None:
    """Verify non-retryable business error mapping."""
    conflict_transport, conflict_session, _, _ = _transport(
        [FakeResponse(409, {"detail": "Already paid"})]
    )
    with pytest.raises(APIConflictError):
        await conflict_transport.request(
            APIOperation.PAY_ORDER,
            json_body={"custom_id": "duplicate"},
        )
    assert len(conflict_session.calls) == 1

    totp_transport, totp_session, _, _ = _transport(
        [FakeResponse(428, {"detail": "TOTP required"})]
    )
    with pytest.raises(APITotpRequiredError):
        await totp_transport.request(
            APIOperation.PAY_ORDER,
            json_body={"custom_id": "requires-totp"},
        )
    assert len(totp_session.calls) == 1


@pytest.mark.asyncio
async def test_rate_limit_uses_retry_after_for_safe_operation() -> None:
    """Verify Retry-After handling without retrying unsafe calls."""
    transport, session, clock, _ = _transport(
        [
            FakeResponse(
                429,
                {"detail": "Slow down"},
                headers={"Retry-After": "3.5"},
            ),
            FakeResponse(200, {"apps": []}),
        ]
    )

    result = await transport.request(APIOperation.STEAM_GIFT_APPS)

    assert result == {"apps": []}
    assert len(session.calls) == 2
    assert clock.sleeps[0] == 3.5


@pytest.mark.asyncio
async def test_retry_after_is_bounded() -> None:
    """Do not suspend a caller indefinitely for a large server delay."""
    transport, _, clock, _ = _transport(
        [
            FakeResponse(
                429,
                {"detail": "Slow down"},
                headers={"Retry-After": "300"},
            ),
            FakeResponse(200, {"apps": []}),
        ]
    )

    await transport.request(APIOperation.STEAM_GIFT_APPS)

    assert clock.sleeps[0] == 30.0


@pytest.mark.asyncio
async def test_injected_session_is_not_closed_by_transport() -> None:
    """Verify that callers retain ownership of injected sessions."""
    transport, session, _, _ = _transport([])
    await transport.close()
    assert session.closed is False
