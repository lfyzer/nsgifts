"""API methods package.

This package contains all API method definitions organized by functionality.
Each module represents a specific domain of the NS Gifts API:

- ip_whitelist: IP whitelist management functionality
- user: User management, authentication, and profile operations
- services: Service listings, categories, and product information
- orders: Order creation, payment, and status tracking
- steam: Steam-specific operations including gifts and currency calculations

Usage:
    from nsgifts_api.methods import UserMethods, ServicesMethods
"""

from .ip_whitelist import IPWhitelistMethods
from .orders import OrderMethods
from .services import ServicesMethods
from .steam import SteamMethods
from .user import UserMethods

__all__ = [
    "UserMethods",
    "ServicesMethods", 
    "OrderMethods",
    "SteamMethods",
    "IPWhitelistMethods",
]
