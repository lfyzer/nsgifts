"""Steam operation models."""

from typing import Optional
from pydantic import BaseModel

from .common import Region


class SteamRubCalculate(BaseModel):
    """Calculate Steam amount from rubles.
    
    Attributes:
        amount (int): Rubles to convert to Steam wallet.
    """
    
    amount: int


class SteamGiftOrderCalculate(BaseModel):
    """Calculate Steam gift pricing.
    
    Check how much a Steam gift costs before ordering it.
    
    Note:
        Rate limited to 1 request per 60 seconds.

    Attributes:
        sub_id (int): Steam package ID (find it in Steam store URLs).
        region (Region): Which region's pricing to use.
    """
    
    sub_id: int
    region: Region


class SteamGiftOrder(BaseModel):
    """Create Steam gift order.

    Send a Steam game as a gift to friend.

    Attributes:
        friendLink (str): Friend's Steam profile URL.
        sub_id (int): Steam package ID to gift.
        region (Region): Target region for pricing.
        giftName (Optional[str]): Custom gift title (optional).
        giftDescription (Optional[str]): Personal message for friend (optional).
    """

    friendLink: str
    sub_id: int
    region: Region
    giftName: Optional[str]
    giftDescription: Optional[str]