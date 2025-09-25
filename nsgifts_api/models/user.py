"""User authentication models."""

from pydantic import BaseModel, Field


class UserLoginSchema(BaseModel):
    """User login data.
    
    Attributes:
        email: Your email or username.
        password: Your password.
    """
    
    email: str = Field(..., example="test")
    password: str = Field(..., example="test")


class UserSchema(BaseModel):
    """User registration data.
    
    Attributes:
        email: Email address (must be unique).
        password: User password.
        bybit_deposit: Initial deposit amount (default 0).
    """
    
    email: str
    password: str
    bybit_deposit: str = "0"
