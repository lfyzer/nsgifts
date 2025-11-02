"""Enums package for NS Gifts API.

This package contains all enumeration types used throughout the NS Gifts API:

- api: API-related enumerations like content types and auth headers
- endpoints: API endpoint paths grouped by functionality  
- http_methods: HTTP request method types
- status: Status codes for orders, payments, tokens, and logging
- steam: Steam-specific enumerations like regions and currencies
- common: Legacy shared enumerations (deprecated, use steam instead)

Usage:
    from nsgifts_api.enums import Region, HTTPRequestType, OrderStatus
    from nsgifts_api.enums import Endpoint
"""

from .api import AuthHeader, ContentType, ErrorType
from .endpoints import (
    UserEndpoint,
    ServicesEndpoint,
    OrdersEndpoint,
    SteamEndpoint,
    IPWhitelistEndpoint,
    Endpoint,
)
from .http_methods import HTTPRequestType
from .steam import Region


__all__ = [
    "HTTPRequestType",
    "ContentType",
    "AuthHeader",
    "ErrorType",
    "Region",
    "UserEndpoint",
    "ServicesEndpoint",
    "OrdersEndpoint",
    "SteamEndpoint",
    "IPWhitelistEndpoint",
    "Endpoint",
]