"""HMAC signing, token state, and replay protection."""

import asyncio
import base64
import binascii
import hashlib
import hmac
import json
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from pydantic import SecretStr

from .errors import APIConfigurationError


def serialize_json(data: Mapping[str, Any] | None) -> bytes:
    """Serialize a JSON object once for signing and transmission."""
    if data is None:
        return b""
    return json.dumps(
        data,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _wire_value(value: Any) -> str:
    """Return an enum value or plain string for the wire."""
    enum_value = getattr(value, "value", value)
    return str(enum_value)


class HMACSigner:
    """Create API v2 HMAC-SHA256 request signatures."""

    def __init__(self, api_secret: str | SecretStr) -> None:
        """Validate and store a decoded API secret."""
        value = (
            api_secret.get_secret_value()
            if isinstance(api_secret, SecretStr)
            else api_secret
        )
        try:
            decoded = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as error:
            raise APIConfigurationError(
                "api_secret must be valid standard Base64"
            ) from error
        if not decoded:
            raise APIConfigurationError("api_secret cannot be empty")
        self._secret = decoded

    def sign(
        self,
        method: Any,
        path: Any,
        query: str,
        body: bytes,
        timestamp: str,
        token: str | None,
    ) -> str:
        """Sign one exact request representation."""
        parts = [
            _wire_value(method).upper(),
            _wire_value(path),
            query,
            timestamp,
        ]
        if token is not None:
            parts.append(token)
        parts.append(hashlib.sha256(body).hexdigest())
        value = "\n".join(parts).encode("utf-8")
        digest = hmac.new(
            self._secret,
            value,
            hashlib.sha256,
        ).digest()
        return base64.b64encode(digest).decode("ascii")


def request_fingerprint(
    method: Any,
    path: Any,
    query: str,
    body: bytes,
    token: str | None,
) -> bytes:
    """Build a secret-free identity for replay timestamp allocation."""
    parts = [
        _wire_value(method).upper(),
        _wire_value(path),
        query,
        token or "",
        hashlib.sha256(body).hexdigest(),
    ]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).digest()


@dataclass(slots=True)
class _ReplayEntry:
    """Per-signature replay state."""

    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    last_timestamp: int = -1
    last_used: float = 0.0


class ReplayGuard:
    """Allocate unique second timestamps for identical requests."""

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.time,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        """Initialize replay tracking with injectable time functions."""
        self._clock = clock
        self._sleeper = sleeper
        self._entries: dict[bytes, _ReplayEntry] = {}
        self._entries_lock = asyncio.Lock()

    async def _entry_for(
        self,
        fingerprint: bytes,
    ) -> _ReplayEntry:
        """Return the independently locked state for a fingerprint."""
        async with self._entries_lock:
            now = self._clock()
            stale = [
                key
                for key, entry in self._entries.items()
                if not entry.lock.locked() and now - entry.last_used > 120
            ]
            for key in stale:
                self._entries.pop(key, None)
            return self._entries.setdefault(
                fingerprint,
                _ReplayEntry(last_used=now),
            )

    async def timestamp_for(self, fingerprint: bytes) -> str:
        """Return a timestamp not yet used for this request identity."""
        entry = await self._entry_for(fingerprint)
        async with entry.lock:
            current = int(self._clock())
            while current <= entry.last_timestamp:
                delay = entry.last_timestamp + 1 - self._clock()
                await self._sleeper(max(delay, 0.001))
                current = int(self._clock())
            entry.last_timestamp = current
            entry.last_used = self._clock()
            return str(current)


@dataclass(frozen=True, slots=True)
class TokenState:
    """In-memory session token and monotonic expiry state."""

    token: SecretStr
    expires_at: float

    @classmethod
    def issue(
        cls,
        *,
        token: str,
        expires_in: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> "TokenState":
        """Create token state from a relative server TTL."""
        return cls(
            token=SecretStr(token),
            expires_at=clock() + expires_in,
        )

    @property
    def value(self) -> str:
        """Return the token for internal header and signature use."""
        return self.token.get_secret_value()

    def is_expiring(
        self,
        buffer_seconds: int,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> bool:
        """Return whether the token is within its refresh window."""
        return self.expires_at - clock() <= buffer_seconds
