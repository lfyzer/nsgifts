"""Common models."""

from pydantic import BaseModel


class PayOrder(BaseModel):
    """Payment request.
    
    Attributes:
        custom_id (str): Order ID to pay for.
    """
    
    custom_id: str


class IPWhitelistRequest(BaseModel):
    """IP whitelist management request.
    
    Attributes:
        ip (str): IP address to add or remove from whitelist.
    """
    
    ip: str
