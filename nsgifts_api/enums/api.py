"""API wire-value enumerations."""

from enum import Enum, IntEnum


class ContentType(str, Enum):
    """Supported HTTP content types."""

    JSON = "application/json"


class HeaderName(str, Enum):
    """Signed request header names."""

    CONTENT_TYPE = "Content-Type"
    SIGNATURE = "X-Signature"
    TIMESTAMP = "X-Timestamp"
    TOKEN = "X-Token"
    USER_AGENT = "User-Agent"
    USER_ID = "X-User-Id"


class APIOperation(str, Enum):
    """Stable operation names used by transport retry policy."""

    GET_TOKEN = "get_token"
    STOCK = "stock"
    CREATE_ORDER = "create_order"
    PAY_ORDER = "pay_order"
    ORDER_INFO = "order_info"
    EXCHANGE_RATE = "exchange_rate"
    CHECK_BALANCE = "check_balance"
    STEAM_GIFT_APPS = "steam_gift_apps"
    STEAM_CHECK_USER = "steam_check_user"


class StockFieldType(str, Enum):
    """Dynamic field types returned by the stock endpoint."""

    STRING = "string"
    INTEGER = "int"
    NUMBER = "float"
    BOOLEAN = "bool"
    ENUM = "enum"


class CreationStatus(str, Enum):
    """Order creation statuses returned by API v2."""

    CREATED = "created"


class PaymentStatus(str, Enum):
    """Payment result statuses returned by API v2."""

    COMPLETED = "completed"
    REFUNDED = "refunded"
    IN_PROGRESS = "in_progress"
    INSUFFICIENT = "insufficient"


class OrderStatus(IntEnum):
    """Order status codes returned by the order-info endpoint."""

    CREATED = 0
    COMPLETED = 2
    CANCELLED = 5
    REFUNDED = 7
    IN_PROGRESS = 10
