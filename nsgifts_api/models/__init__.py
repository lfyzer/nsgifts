"""Data models package.

This package contains all Pydantic data models used for API request/response
validation and serialization. Models are organized by functionality:

- common: Shared models and enums used across multiple endpoints
- user: User authentication and profile models  
- services: Service and category-related models
- orders: Order creation and management models
- steam: Steam-specific operation models

Usage:
    from nsgifts_api.models import Region, UserLoginSchema, CreateOrder
"""

from .common import Region, PayOrder, IPWhitelistRequest
from .user import UserLoginSchema, UserSchema
from .services import (
    CategoryRequest,
    CategoryItem,
    ServiceItem,
    GetServicesResponseModel,
)
from .orders import CreateOrder
from .steam import (
    SteamRubCalculate,
    SteamGiftOrderCalculate,
    SteamGiftOrder,
)

__all__ = [
    # Common models
    "Region",
    "PayOrder",
    "IPWhitelistRequest",
    # User models
    "UserLoginSchema", 
    "UserSchema",
    # Service models
    "CategoryRequest",
    "CategoryItem",
    "ServiceItem", 
    "GetServicesResponseModel",
    # Order models
    "CreateOrder",
    # Steam models
    "SteamRubCalculate",
    "SteamGiftOrderCalculate", 
    "SteamGiftOrder",
]
