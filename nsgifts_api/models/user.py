"""User authentication models."""

from pydantic import BaseModel


class UserLoginSchema(BaseModel):
    """User login data.
    
    Attributes:
        email (str): Your email or username.
        password (str): Your password.
    """
    
    email: str
    password: str


class UserSignupSchema(BaseModel):
    """User signup data.
    
    Attributes:
        username (str): Username (must be unique).
        password (str): User password.
        email (str): Email address (must be unique).
    """
    
    username: str
    password: str
    email: str


class UserSchema(BaseModel):
    """User registration data.
    
    Attributes:
        email (str): Email address (must be unique).
        role (str): User role.
        bybit_deposit (str): Initial deposit amount (default 0).
    """
    
    email: str
    role: str
    bybit_deposit: str = "0"
