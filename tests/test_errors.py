"""Tests for safe HTTP error mapping."""

from nsgifts_api.errors import (
    APIAuthenticationError,
    APIClockSkewError,
    APIConflictError,
    APIIPNotAllowedError,
    APIRateLimitError,
    APITotpRequiredError,
    APIValidationError,
    from_http_status,
)


def test_sensitive_response_fields_are_redacted() -> None:
    """Verify recursive redaction in exception details."""
    error = from_http_status(
        400,
        response_data={
            "detail": "bad request",
            "password": "visible-password",
            "nested": {"token": "visible-token"},
        },
    )
    rendered = str(error)
    assert "visible-password" not in rendered
    assert "visible-token" not in rendered
    assert rendered.count("[REDACTED]") == 2


def test_embedded_and_noncanonical_secrets_are_redacted() -> None:
    """Redact known values in messages and common secret-key variants."""
    token = "session-token-value"
    api_secret = "api-secret-value"
    error = from_http_status(
        401,
        response_data={
            "detail": f"Invalid token {token}",
            "access_token": token,
            "apiSecret": api_secret,
        },
        sensitive_values=(token, api_secret),
    )

    rendered = str(error)
    assert token not in rendered
    assert api_secret not in rendered
    assert rendered.count("[REDACTED]") >= 3


def test_authentication_errors_are_specialized() -> None:
    """Verify timestamp and normal authentication mappings."""
    skew = from_http_status(
        401,
        response_data={"detail": "Timestamp outside allowed window"},
    )
    regular = from_http_status(
        401,
        response_data={"detail": "Invalid session token"},
    )
    assert isinstance(skew, APIClockSkewError)
    assert isinstance(regular, APIAuthenticationError)


def test_ip_whitelist_and_totp_errors_are_specialized() -> None:
    """Verify actionable forbidden and TOTP exceptions."""
    ip_error = from_http_status(
        403,
        response_data={"detail": "IP is not in whitelist"},
    )
    totp_error = from_http_status(
        428,
        response_data={"detail": "TOTP required"},
    )
    assert isinstance(ip_error, APIIPNotAllowedError)
    assert isinstance(totp_error, APITotpRequiredError)


def test_validation_conflict_and_rate_limit_mapping() -> None:
    """Verify non-retryable and rate-limit exceptions."""
    validation = from_http_status(422)
    conflict = from_http_status(409)
    rate_limit = from_http_status(429, retry_after=3.5)
    assert isinstance(validation, APIValidationError)
    assert isinstance(conflict, APIConflictError)
    assert isinstance(rate_limit, APIRateLimitError)
    assert rate_limit.retry_after == 3.5
