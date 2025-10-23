from typing import Optional
from pydantic import BaseModel, Field, validator
import re

from ..enums import SteamRegion


class SteamRubCalculate(BaseModel):
    amount: int = Field(..., gt=0)


class SteamGiftOrderCalculate(BaseModel):
    sub_id: int = Field(..., gt=0, alias="subId")
    region: SteamRegion
    
    class Config:
        allow_population_by_field_name = True


class SteamGiftOrder(BaseModel):
    # я днем говорил. вот преобразование в snake_case
    # в маппинге нужно добавить .model_dump(by_alias=True)
    friend_link: str = Field(..., min_length=1, max_length=500, alias="friendLink")
    sub_id: int = Field(..., gt=0, alias="subId")
    region: SteamRegion
    gift_name: Optional[str] = Field(None, max_length=100, alias="giftName")
    gift_description: Optional[str] = Field(None, max_length=500, alias="giftDescription")
    
    @validator('friend_link')
    def validate_steam_url(cls, v):
        steam_patterns = [
            # дипсик писал, проверь
            r'https://steamcommunity\.com/id/[^/]+/?',
            r'https://steamcommunity\.com/profiles/\d+/?',
        ]
        if not any(re.match(pattern, v) for pattern in steam_patterns):
            raise ValueError('Invalid Steam profile URL format')
        return v
    
    class Config:
        allow_population_by_field_name = True