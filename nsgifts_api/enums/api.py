from enum import Enum


class ContentType(str, Enum):
    JSON = "application/json"
    MULTIPART = "multipart/form-data" # в коде не видел, но думаю что понадобится


class AuthHeader(str, Enum):
    BEARER = "Bearer"


class ErrorType(str, Enum):
    CONNECTION = "connection"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    CLIENT = "client"
    SERVER = "server"
