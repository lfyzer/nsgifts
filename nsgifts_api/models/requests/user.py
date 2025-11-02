"""User API request models."""

from pydantic import BaseModel, Field


class UserLoginSchema(BaseModel):
    """User login request.
    
    Attributes:
        email (str): Your email or username.
        password (str): Your password.
    """
    
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)


class UserSignupSchema(BaseModel):
    """User signup request.
    
    Attributes:
        username (str): Username (must be unique).
        password (str): User password.
        email (str): Email address (must be unique).
    """
    
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)


class UserSchema(BaseModel):
    """User registration request.
    
    Attributes:
        email (str): Email address (must be unique).
        role (str): User role.
        bybit_deposit (str): Initial deposit amount (default 0).
    """
    
    email: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=50)
    bybit_deposit: str = Field(default="0", pattern=r'^\d+(\.\d+)?$')
