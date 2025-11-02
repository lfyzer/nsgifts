"""NS Gifts API Client.

Simple Python client for NS Gifts API operations.
"""

__version__ = "1.1.0"
__author__ = "lfyzer"
__license__ = "MIT"

from .client import NSGiftsClient
from .config import ClientConfig
from .enums import Region
from .errors import (
    APIAuthenticationError,
    APIClientError,
    APIConnectionError,
    APIError,
    APIInsufficientFundsError,
    APINotFoundError,
    APIRateLimitError,
    APIServerError,
    APITimeoutError,
    APIValidationError,
    from_http_status,
)
from .models import (
    # Common models
    IPWhitelistRequest,
    PayOrder,
    # User models
    LoginResponse,
    SignupResponse,
    UserInfoResponse,
    UserLoginSchema,
    UserSchema,
    UserSignupSchema,
    # Service models (catalog requests)
    CategoryRequest,
    # Order models
    CreateOrder,
    OrderResponse,
    PaymentResponse,
    OrderInfoResponse,
    # Steam models
    SteamAmountResponse,
    SteamCurrencyRateResponse,
    SteamGiftCalculateResponse,
    SteamGiftOrder,
    SteamGiftOrderCalculate,
    SteamGiftOrderResponse,
    SteamRubCalculate,
    # IP whitelist responses
    IPWhitelistAddResponse,
    IPWhitelistRemoveResponse,
)

__all__ = [
    # Version info
    "__version__",
    
    # Main client
    "NSGiftsClient",
    
    # Configuration
    "ClientConfig",
    
    # Exceptions
    "APIError",
    "APIConnectionError",
    "APITimeoutError",
    "APIAuthenticationError",
    "APIValidationError",
    "APIRateLimitError",
    "APINotFoundError",
    "APIInsufficientFundsError",
    "APIServerError", 
    "APIClientError",
    "from_http_status",
    
    # Enums
    "Region",
    
    # Common models
    "PayOrder",
    "IPWhitelistRequest",
    
    # User models
    "UserLoginSchema",
    "UserSignupSchema",
    "UserSchema",
    "LoginResponse",
    "SignupResponse",
    "UserInfoResponse",
    
    # Service models  
    "CategoryRequest",
    
    # Order models
    "CreateOrder",
    "OrderResponse",
    "PaymentResponse",
    "OrderInfoResponse",

    # Steam models
    "SteamRubCalculate",
    "SteamAmountResponse",
    "SteamCurrencyRateResponse",
    "SteamGiftOrderCalculate",
    "SteamGiftCalculateResponse",
    "SteamGiftOrder",
    "SteamGiftOrderResponse",
    # IP whitelist responses
    "IPWhitelistAddResponse",
    "IPWhitelistRemoveResponse",
]
