"""Data models package.

This package contains all Pydantic data models used for API request/response
validation and serialization. Models are organized by functionality:

- common: Shared models used across multiple endpoints
- user: User authentication and profile models  
- services: Service and category-related models
- orders: Order creation and management models
- steam: Steam-specific operation models

Usage:
    from nsgifts_api.models import UserLoginSchema, CreateOrder
    from nsgifts_api.enums import Region, OrderStatus
"""

from .common import IPWhitelistRequest, PayOrder
from .orders import CreateOrder
from .services import CategoryRequest
from .steam import (
    SteamGiftOrder,
    SteamGiftOrderCalculate,
    SteamRubCalculate,
)
from .user import UserLoginSchema, UserSchema, UserSignupSchema

__all__ = [
    # Common models
    "PayOrder",
    "IPWhitelistRequest",
    # User models
    "UserLoginSchema", 
    "UserSignupSchema",
    "UserSchema",
    # Service models
    "CategoryRequest",
    # Order models
    "CreateOrder",
    # Steam models
    "SteamRubCalculate",
    "SteamGiftOrderCalculate", 
    "SteamGiftOrder",
]
