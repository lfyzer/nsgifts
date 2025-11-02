"""Data models package.

This package contains all Pydantic data models used for API
request/response validation and serialization. Models are organized by
functionality and separated into requests and responses:

Request Models:
- requests.ip_whitelist: IP whitelist management requests
- requests.user: User authentication requests  
- requests.services: Service-related requests
- requests.orders: Order creation requests
- requests.steam: Steam operation requests

Response Models:
- responses.ip_whitelist: IP whitelist management responses
- responses.user: User authentication responses
- responses.services: Service-related responses
- responses.orders: Order management responses
- responses.steam: Steam operation responses

Usage:
    from nsgifts_api.models.requests.user import UserLoginSchema
    from nsgifts_api.models.responses.user import LoginResponse
    from nsgifts_api.models.requests.orders import CreateOrder
    from nsgifts_api.models.responses.orders import OrderResponse
"""

# Import all request models
from .requests.ip_whitelist import IPWhitelistRequest
from .requests.orders import CreateOrder, PayOrder
from .requests.services import CategoryRequest
from .requests.steam import (
    SteamGiftOrder,
    SteamGiftOrderCalculate,
    SteamRubCalculate,
)
from .requests.user import UserLoginSchema, UserSchema, UserSignupSchema

# Import all response models
from .responses.ip_whitelist import (
    IPWhitelistAddResponse,
    IPWhitelistRemoveResponse,
)
from .responses.orders import OrderResponse, PaymentResponse, OrderInfoResponse

from .responses.steam import (
    SteamAmountResponse,
    SteamCurrencyRateResponse,
    SteamGiftCalculateResponse,
    SteamGiftOrderResponse,
)
from .responses.user import LoginResponse, SignupResponse, UserInfoResponse

__all__ = [
    # Request models
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
    # Response models
    "IPWhitelistAddResponse",
    "IPWhitelistRemoveResponse",
    "LoginResponse",
    "SignupResponse",
    "UserInfoResponse",
    "ServiceItem",
    "OrderResponse",
    "PaymentResponse",
    "OrderInfoResponse",
    "SteamAmountResponse",
    "SteamCurrencyRateResponse",
    "SteamGiftCalculateResponse",
    "SteamGiftOrderResponse",
]