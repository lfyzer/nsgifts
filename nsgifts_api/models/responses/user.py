"""User API response models."""

from typing import Optional

from pydantic import BaseModel


class LoginResponse(BaseModel):
    """Login response with access token.
    
    Attributes:
        access_token (str): JWT access token.
        valid_thru (int): Token expiration timestamp.
        user_id (int): User ID.
    """
    
    access_token: str
    valid_thru: int
    user_id: int


class SignupResponse(BaseModel):
    """Signup response with access token.
    
    Attributes:
        access_token (str): JWT access token.
        token_type (str): Token type (bearer).
    """
    
    access_token: str
    token_type: str


class UserInfoResponse(BaseModel):
    """User profile information.
    
    Attributes:
        id (int): User ID.
        username (Optional[str]): Username (can be None).
        login (Optional[str]): Login name.
        rights (list): User rights/roles list.
        balance (float): Account balance.
    """
    
    id: int
    username: Optional[str] = None
    login: Optional[str] = None
    rights: list = []
    balance: float
