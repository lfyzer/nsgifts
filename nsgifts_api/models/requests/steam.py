"""Steam API request models."""

from typing import Optional
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ...enums import Region


class SteamRubCalculate(BaseModel):
    """Calculate Steam amount from rubles.
    
    Attributes:
        amount (int): Rubles to convert to Steam wallet.
    """
    
    amount: int = Field(..., gt=0)


class SteamGiftOrderCalculate(BaseModel):
    """Calculate Steam gift pricing.
    
    Check how much a Steam gift costs before ordering it.
    
    Note:
        Rate limited to 1 request per 60 seconds.

    Attributes:
        sub_id (int): Steam package ID (find it in Steam store URLs).
        region (Region): Which region's pricing to use.
    """
    
    model_config = ConfigDict(populate_by_name=True)
    sub_id: int = Field(..., gt=0, alias="subId")
    region: Region


class SteamGiftOrder(BaseModel):
    """Create Steam gift order.

    Send a Steam game as a gift to friend.

    Attributes:
        friend_link (str): Friend's Steam profile URL.
        sub_id (int): Steam package ID to gift.
        region (Region): Target region for pricing.
        gift_name (Optional[str]): Custom gift title (optional).
        gift_description (Optional[str]): Personal message (optional).
    """

    friend_link: str = Field(
        ..., min_length=1, max_length=500, alias="friendLink"
    )
    sub_id: int = Field(..., gt=0)
    region: Region
    gift_name: Optional[str] = Field(
        None, max_length=100, alias="giftName"
    )
    gift_description: Optional[str] = Field(
        None, max_length=500, alias="giftDescription"
    )
    
    @field_validator("friend_link")
    @classmethod
    def validate_steam_url(cls, v: str) -> str:
        """Validate Steam profile URL format.
        
        Args:
            v: URL string to validate.
            
        Returns:
            Validated URL string.
            
        Raises:
            ValueError: If URL format is invalid.
        """

        pattern = r"https?://s\.team/p/[^\s]*"
        if not re.match(pattern, v):
            raise ValueError('Invalid Steam profile URL format')
        return v