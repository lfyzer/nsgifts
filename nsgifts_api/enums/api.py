"""API-related enumerations."""

from enum import Enum


class ContentType(str, Enum):
    """HTTP Content-Type headers.
    
    Attributes:
        JSON: Application JSON content type.
        MULTIPART: Multipart form data content type. Not need now
    """
    
    JSON = "application/json"
    #MULTIPART = "multipart/form-data"


class AuthHeader(str, Enum):
    """Authentication header types.
    
    Attributes:
        BEARER: Bearer token authentication.
    """
    
    BEARER = "Bearer"


class ErrorType(str, Enum):
    """Error type categories.
    
    Attributes:
        CONNECTION: Connection-related errors.
        TIMEOUT: Request timeout errors.
        AUTHENTICATION: Authentication failures.
        CLIENT: Client-side errors (4xx).
        SERVER: Server-side errors (5xx).
    """
    
    CONNECTION = "connection"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    CLIENT = "client"
    SERVER = "server"