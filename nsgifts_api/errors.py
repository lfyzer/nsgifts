"""Exceptions and safe error mapping for NS.Gifts API v2."""

from collections.abc import Iterable, Mapping
from typing import Any

_SENSITIVE_KEYS = frozenset(
    {
        "access_token",
        "api_secret",
        "authorization",
        "client_secret",
        "password",
        "refresh_token",
        "signature",
        "token",
        "totp_code",
        "x-signature",
        "x-token",
    }
)


def _is_sensitive_key(value: object) -> bool:
    """Return whether a response key commonly contains a credential."""
    normalized = "".join(
        character for character in str(value).lower() if character.isalnum()
    )
    keys = {
        "".join(character for character in key if character.isalnum())
        for key in _SENSITIVE_KEYS
    }
    return normalized in keys or normalized.endswith(
        ("password", "secret", "signature", "token", "totpcode")
    )


def _redact_text(value: str, sensitive_values: tuple[str, ...]) -> str:
    """Remove known secret values embedded in a diagnostic message."""
    result = value
    for secret in sorted(set(sensitive_values), key=len, reverse=True):
        if secret:
            result = result.replace(secret, "[REDACTED]")
    return result


def _redact_sensitive(
    value: Any,
    sensitive_values: tuple[str, ...],
) -> Any:
    """Recursively redact known values and credential-bearing fields."""
    if isinstance(value, Mapping):
        return {
            key: (
                "[REDACTED]"
                if _is_sensitive_key(key)
                else _redact_sensitive(item, sensitive_values)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_sensitive(item, sensitive_values) for item in value]
    if isinstance(value, tuple):
        return tuple(
            _redact_sensitive(item, sensitive_values) for item in value
        )
    if isinstance(value, str):
        return _redact_text(value, sensitive_values)
    return value


def redact_sensitive(
    value: Any,
    *,
    sensitive_values: Iterable[str] = (),
) -> Any:
    """Recursively redact credentials from diagnostic data."""
    return _redact_sensitive(value, tuple(sensitive_values))


class APIError(Exception):
    """Base exception for all client and server errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        """Initialize a safe API exception."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = redact_sensitive(dict(details or {}))

    def __str__(self) -> str:
        """Render the error without secret request data."""
        prefix = (
            f"[{self.status_code}] " if self.status_code is not None else ""
        )
        if self.details:
            return f"{prefix}{self.message} | Details: {self.details}"
        return f"{prefix}{self.message}"


class APIConfigurationError(APIError):
    """Raised when local client configuration is invalid."""


class APIConnectionError(APIError):
    """Raised when the API connection cannot be established."""


class APITimeoutError(APIError):
    """Raised when an API request exceeds its timeout."""


class APIAuthenticationError(APIError):
    """Raised when HMAC or session-token authentication fails."""


class APIClockSkewError(APIAuthenticationError):
    """Raised when the request timestamp differs from server time."""


class APIForbiddenError(APIError):
    """Raised when the account lacks access to an operation."""


class APIIPNotAllowedError(APIForbiddenError):
    """Raised when the request IP is absent from the whitelist."""


class APIValidationError(APIError):
    """Raised when request data fails server validation."""


class APIRateLimitError(APIError):
    """Raised when the server rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        *,
        retry_after: float | None = None,
        status_code: int = 429,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        """Initialize a rate-limit error."""
        super().__init__(
            message,
            status_code=status_code,
            details=details,
        )
        self.retry_after = retry_after


class APINotFoundError(APIError):
    """Raised when an order, service, or endpoint is not found."""


class APIInsufficientFundsError(APIError):
    """Raised when the account balance cannot cover a payment."""


class APIConflictError(APIError):
    """Raised for duplicate orders or repeated payments."""


class APITotpRequiredError(APIAuthenticationError):
    """Raised when payment requires a six-digit TOTP code."""


class APIServerError(APIError):
    """Raised for an NS.Gifts server-side failure."""


class APIClientError(APIError):
    """Raised for an otherwise unclassified client-side failure."""


class APIRequestOutcomeUnknownError(APIError):
    """Raised when an unsafe request may have reached the server."""

    def __init__(
        self,
        operation: str,
        *,
        custom_id: str | None,
        cause: BaseException,
    ) -> None:
        """Initialize an uncertain-outcome exception."""
        message = (
            f"Outcome of {operation} is unknown; "
            "check order_info before retrying"
        )
        super().__init__(
            message,
            details={
                "operation": operation,
                "custom_id": custom_id,
                "cause_type": type(cause).__name__,
            },
        )
        self.operation = operation
        self.custom_id = custom_id


def _response_message(
    response_data: Mapping[str, Any] | None,
    fallback: str,
) -> str:
    """Extract a concise message from an API error response."""
    if not response_data:
        return fallback
    for key in ("message", "detail", "error"):
        value = response_data.get(key)
        if isinstance(value, str) and value:
            return value
    return fallback


def from_http_status(
    status_code: int,
    message: str | None = None,
    response_data: Mapping[str, Any] | None = None,
    *,
    retry_after: float | None = None,
    sensitive_values: Iterable[str] = (),
) -> APIError:
    """Create a typed exception from an HTTP status code."""
    secrets = tuple(sensitive_values)
    fallback = _redact_text(message or f"HTTP {status_code}", secrets)
    safe_response: Mapping[str, Any] = redact_sensitive(
        dict(response_data or {}),
        sensitive_values=secrets,
    )
    text = _response_message(safe_response, fallback)
    lowered = text.lower()
    details = {"response": safe_response}

    if status_code == 401:
        if "timestamp" in lowered or "clock" in lowered:
            return APIClockSkewError(
                text,
                status_code=status_code,
                details=details,
            )
        if "totp" in lowered or "2fa" in lowered:
            return APITotpRequiredError(
                text,
                status_code=status_code,
                details=details,
            )
        return APIAuthenticationError(
            text,
            status_code=status_code,
            details=details,
        )
    if status_code == 403:
        error_class = (
            APIIPNotAllowedError
            if "ip" in lowered or "whitelist" in lowered
            else APIForbiddenError
        )
        return error_class(
            text,
            status_code=status_code,
            details=details,
        )
    if status_code == 404:
        return APINotFoundError(
            text,
            status_code=status_code,
            details=details,
        )
    if status_code == 409:
        return APIConflictError(
            text,
            status_code=status_code,
            details=details,
        )
    if status_code == 428:
        return APITotpRequiredError(
            text,
            status_code=status_code,
            details=details,
        )
    if status_code == 429:
        return APIRateLimitError(
            text,
            retry_after=retry_after,
            details=details,
        )
    if status_code == 402:
        return APIInsufficientFundsError(
            text,
            status_code=status_code,
            details=details,
        )
    if status_code in {400, 422}:
        return APIValidationError(
            text,
            status_code=status_code,
            details=details,
        )
    if 400 <= status_code < 500:
        return APIClientError(
            text,
            status_code=status_code,
            details=details,
        )
    if 500 <= status_code < 600:
        return APIServerError(
            text,
            status_code=status_code,
            details=details,
        )
    return APIError(
        text,
        status_code=status_code,
        details=details,
    )
