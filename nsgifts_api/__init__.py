"""NS Gifts API Client.

Simple Python client for NS Gifts API operations.
"""

from .client import NSGiftsClient
from .enums import (
    Region,
)
from .errors import (
    APIAuthenticationError,
    APIClientError,
    APIConnectionError,
    APIError,
    APIServerError,
    APITimeoutError,
)
from .models import (
    # Common models
    IPWhitelistRequest,
    PayOrder,
    # User models
    UserLoginSchema,
    UserSchema,
    UserSignupSchema,
    # Service models
    CategoryRequest,
    # Order models
    CreateOrder,
    # Steam models
    SteamGiftOrder,
    SteamGiftOrderCalculate,
    SteamRubCalculate,
)

__all__ = [
    # Main client
    "NSGiftsClient",
    
    # Exceptions
    "APIError",
    "APIConnectionError",
    "APITimeoutError",
    "APIAuthenticationError",
    "APIServerError", 
    "APIClientError",
    
    # Enums
    "Region"
    
    # Common models
    "PayOrder",
    "IPWhitelistRequest",
    
    # User models
    "UserLoginSchema",
    "UserSignupSchema",
    "UserSchema",
    
    # Service models  
    "CategoryRequest"
    
    # Order models
    "CreateOrder"
    
    # Steam models
    "SteamRubCalculate",
    "SteamGiftOrderCalculate", 
    "SteamGiftOrder",
]
