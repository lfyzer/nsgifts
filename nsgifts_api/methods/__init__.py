"""High-level NS.Gifts API v2 method groups."""

from .account import AccountMethods
from .catalog import CatalogMethods
from .orders import OrderMethods
from .steam import SteamMethods

__all__ = [
    "AccountMethods",
    "CatalogMethods",
    "OrderMethods",
    "SteamMethods",
]
