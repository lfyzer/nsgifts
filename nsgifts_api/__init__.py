"""NS Gifts API Client.

Simple Python client for NS Gifts API operations.
"""

from .client import NSGiftsClient
from .errors import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    APIAuthenticationError,
    APIServerError,
    APIClientError,
)
from .models import (
    # Common models
    Region,
    PayOrder,
    # User models
    UserLoginSchema,
    UserSchema,
    # Service models
    CategoryRequest,
    CategoryItem,
    ServiceItem,
    GetServicesResponseModel,
    # Order models
    CreateOrder,
    # Steam models
    SteamRubCalculate,
    SteamGiftOrderCalculate,
    SteamGiftOrder,
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
    
    # Common models
    "Region",
    "PayOrder",
    
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
    "SteamPackageRequest",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__url__",
]