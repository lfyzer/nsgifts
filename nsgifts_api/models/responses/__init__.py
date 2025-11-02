"""Response models package.

This package contains all Pydantic models for API responses.
Each module contains response models for specific functionality:

- ip_whitelist: IP whitelist management responses
- user: User authentication and profile responses
- orders: Order creation and management responses
- steam: Steam-specific operation responses

Usage:
    from nsgifts_api.models.responses.ip_whitelist import IPWhitelistAddResponse
    from nsgifts_api.models.responses.user import LoginResponse
    from nsgifts_api.models.responses.orders import OrderResponse
    from nsgifts_api.models.responses.steam import SteamGiftOrderResponse
"""

from .ip_whitelist import (
    IPWhitelistAddResponse,
    IPWhitelistRemoveResponse,
)
from .orders import OrderResponse, PaymentResponse, OrderInfoResponse
from .steam import (
    SteamAmountResponse,
    SteamCurrencyRateResponse,
    SteamGiftCalculateResponse,
    SteamGiftOrderResponse,
)
from .user import LoginResponse, SignupResponse, UserInfoResponse

__all__ = [
    "IPWhitelistAddResponse",
    "IPWhitelistRemoveResponse",
    "LoginResponse",
    "SignupResponse",
    "UserInfoResponse",
    "OrderResponse",
    "PaymentResponse",
    "OrderInfoResponse",
    "SteamAmountResponse",
    "SteamCurrencyRateResponse",
    "SteamGiftCalculateResponse",
    "SteamGiftOrderResponse",
]