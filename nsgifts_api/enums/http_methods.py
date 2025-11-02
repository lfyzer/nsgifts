"""HTTP methods enumeration."""

from enum import Enum


class HTTPRequestType(str, Enum):
    """HTTP request methods.
    
    Attributes:
        GET: HTTP GET method. not used now
        POST: HTTP POST method.
        PUT: HTTP PUT method. not used now
        DELETE: HTTP DELETE method. not used now
        PATCH: HTTP PATCH method. not used now
    """
    
    # GET = "GET"
    POST = "POST"
    # PUT = "PUT"
    # DELETE = "DELETE"
    # PATCH = "PATCH"