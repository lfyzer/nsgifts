"""Secure client configuration for NS.Gifts API v2."""

from pathlib import Path
from typing import Any

from pydantic import (
    AnyHttpUrl,
    Field,
    SecretStr,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientConfig(BaseSettings):
    """Validated settings for :class:`NSGiftsClient`.

    Values may be passed directly or loaded from variables prefixed with
    ``NSGIFTS_``. Password and API secret values use ``SecretStr`` so their
    representations remain masked.
    """

    model_config = SettingsConfigDict(
        env_prefix="NSGIFTS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    user_id: int = Field(gt=0)
    login: str = Field(min_length=1, max_length=255)
    password: SecretStr
    api_secret: SecretStr
    base_url: AnyHttpUrl = AnyHttpUrl("https://api.ns.gifts")
    request_timeout: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    token_refresh_buffer: int = Field(default=300, ge=0)
    enable_logging: bool = False
    log_level: str = "INFO"

    @field_validator("base_url")
    @classmethod
    def validate_https(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        """Require HTTPS for all credential-bearing requests."""
        if value.scheme != "https":
            raise ValueError("base_url must use HTTPS")
        return value

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Normalize and validate the library log level."""
        normalized = value.upper()
        valid_levels = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }
        if normalized not in valid_levels:
            raise ValueError(f"log_level must be one of {sorted(valid_levels)}")
        return normalized

    @property
    def normalized_base_url(self) -> str:
        """Return the base URL without a trailing slash."""
        return str(self.base_url).rstrip("/")

    @classmethod
    def from_env(
        cls,
        env_file: str | Path | None = ".env",
    ) -> "ClientConfig":
        """Load configuration from prefixed environment variables.

        Args:
            env_file: Optional dotenv path. Pass ``None`` to use process
                environment variables only.

        Returns:
            A validated client configuration.
        """
        return cls(_env_file=env_file)  # type: ignore[call-arg]

    def to_safe_dict(self) -> dict[str, Any]:
        """Serialize non-secret settings for diagnostics."""
        return {
            "user_id": self.user_id,
            "login": self.login,
            "base_url": self.normalized_base_url,
            "request_timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "token_refresh_buffer": self.token_refresh_buffer,
            "enable_logging": self.enable_logging,
            "log_level": self.log_level,
        }
