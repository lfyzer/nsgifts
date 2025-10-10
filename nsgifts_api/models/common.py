"""Common models and enums."""

from enum import Enum

from pydantic import BaseModel


class Region(str, Enum):
    """Steam regions.
    
    Attributes:
        RU: Russia
        KZ: Kazakhstan  
        UA: Ukraine
    """
    
    RU = "ru"
    KZ = "kz"
    UA = "ua"


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
