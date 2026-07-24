"""Authentication request models."""

from typing import Any

from pydantic import Field, SecretStr

from .base import RequestModel


class TokenRequest(RequestModel):
    """Credentials exchanged for a short-lived session token."""

    login: str = Field(min_length=1, max_length=255)
    password: SecretStr

    def to_payload(self) -> dict[str, Any]:
        """Serialize the real password only at the wire boundary."""
        data = super().to_payload()
        data["password"] = self.password.get_secret_value()
        return data
