"""Authentication response models."""

from pydantic import Field, SecretStr

from .base import ResponseModel


class TokenResponse(ResponseModel):
    """Short-lived token returned by the bootstrap endpoint."""

    user_id: int = Field(gt=0)
    token: SecretStr
    expires_in: int = Field(gt=0)
