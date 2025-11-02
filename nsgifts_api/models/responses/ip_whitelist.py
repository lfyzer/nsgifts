"""Common API response models."""

from pydantic import BaseModel


class IPWhitelistAddResponse(BaseModel):
    """IP whitelist operation response.
    
    Attributes:
        status (str): Operation status.
        added (str): IP address affected.
    """
    
    status: str
    added: str


class IPWhitelistRemoveResponse(BaseModel):
    """IP whitelist operation response.
    
    Attributes:
        status (str): Operation status.
        removed (str): IP address affected.
    """
    
    status: str
    removed: str