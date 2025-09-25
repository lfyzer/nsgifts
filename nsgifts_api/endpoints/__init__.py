"""API endpoints package.

This package contains all API endpoint definitions organized by functionality.
Each module represents a specific domain of the NS Gifts API:

- user: User management, authentication, and profile operations
- services: Service listings, categories, and product information
- orders: Order creation, payment, and status tracking
- steam: Steam-specific operations including gifts and currency calculations
- ip_whitelist: IP whitelist management functionality

Usage:
    from nsgifts_api.endpoints import UserEndpoints, ServicesEndpoints
"""

from .user import UserEndpoints
from .services import ServicesEndpoints  
from .orders import OrderEndpoints
from .steam import SteamEndpoints
from .ip_whitelist import IPWhitelistEndpoints

__all__ = [
    "UserEndpoints",
    "ServicesEndpoints", 
    "OrderEndpoints",
    "SteamEndpoints",
    "IPWhitelistEndpoints",
]
