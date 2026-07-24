"""Order request models for the unified API v2 flow."""

import re
from typing import Any

from pydantic import UUID4, Field, SecretStr, field_validator

from .base import JSONScalar, RequestModel


class OrderField(RequestModel):
    """One dynamic field required by a stock category."""

    key: str = Field(min_length=1, max_length=255)
    value: JSONScalar


class OrderReference(RequestModel):
    """Strict UUID4 reference to a partner order."""

    custom_id: UUID4


class CreateOrderRequest(OrderReference):
    """Unified order-creation request."""

    service_id: int = Field(gt=0)
    fields: list[OrderField] = Field(min_length=1)


class PayOrderRequest(OrderReference):
    """Order-payment request with optional purchase TOTP."""

    totp_code: SecretStr | None = None

    @field_validator("totp_code")
    @classmethod
    def validate_totp(
        cls,
        value: SecretStr | None,
    ) -> SecretStr | None:
        """Require exactly six decimal digits when TOTP is present."""
        if value is not None and not re.fullmatch(
            r"\d{6}",
            value.get_secret_value(),
        ):
            raise ValueError("totp_code must contain six digits")
        return value

    def to_payload(self) -> dict[str, Any]:
        """Serialize the real TOTP only at the wire boundary."""
        data = super().to_payload()
        if self.totp_code is not None:
            data["totp_code"] = self.totp_code.get_secret_value()
        return data
