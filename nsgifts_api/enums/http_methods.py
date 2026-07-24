"""HTTP method enumerations."""

from enum import Enum


class HTTPMethod(str, Enum):
    """HTTP methods used by NS.Gifts API v2."""

    GET = "GET"
    POST = "POST"
