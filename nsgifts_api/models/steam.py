"""Steam operation models."""

from typing import Optional
from pydantic import BaseModel, Field

from .common import Region


class SteamRubCalculate(BaseModel):
    """Calculate Steam amount from rubles.
    
    Attributes:
        amount: Rubles to convert to Steam wallet.
    """
    
    amount: int = Field(..., description="Сумма для расчета")


class SteamGiftOrderCalculate(BaseModel):
    """Calculate Steam gift pricing.
    
    Check how much a Steam gift costs before ordering it.
    
    Note:
        Rate limited to 1 request per 60 seconds.

    Attributes:
        sub_id: Steam package ID (find it in Steam store URLs).
        region: Which region's pricing to use.
    """
    
    sub_id: int
    region: Region


class SteamGiftOrder(BaseModel):
    """Create Steam gift order.
    
    Send a Steam game as a gift to your friend.
    
    Attributes:
        friend_link: Your friend's Steam profile URL.
        sub_id: Steam package ID to gift.
        region: Target region for pricing.
        gift_name: Custom gift title (optional).
        gift_description: Personal message for your friend (optional).
    """
    
    friend_link: str = Field(alias="friendLink")
    sub_id: int
    region: Region
    gift_name: Optional[str] = Field(None, alias="giftName")
    gift_description: Optional[str] = Field(None, alias="giftDescription")
