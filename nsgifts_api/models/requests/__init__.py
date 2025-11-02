"""Request models package.

This package contains all Pydantic models for API requests.
Each module contains request models for specific functionality:

- ip_whitelist: IP whitelist management requests
- user: User authentication and registration requests
- services: Service-related requests
- orders: Order creation and management requests
- steam: Steam-specific operation requests

Usage:
    from nsgifts_api.models.requests.ip_whitelist import IPWhitelistRequest
    from nsgifts_api.models.requests.user import UserLoginSchema
    from nsgifts_api.models.requests.orders import CreateOrder
    from nsgifts_api.models.requests.steam import SteamGiftOrder
"""

from .ip_whitelist import IPWhitelistRequest
from .orders import CreateOrder, PayOrder
from .services import CategoryRequest
from .steam import SteamGiftOrder, SteamGiftOrderCalculate, SteamRubCalculate
from .user import UserLoginSchema, UserSchema, UserSignupSchema

__all__ = [
    "PayOrder",
    "IPWhitelistRequest",
    "UserLoginSchema",
    "UserSignupSchema", 
    "UserSchema",
    "CategoryRequest",
    "CreateOrder",
    "SteamRubCalculate",
    "SteamGiftOrderCalculate",
    "SteamGiftOrder",
]