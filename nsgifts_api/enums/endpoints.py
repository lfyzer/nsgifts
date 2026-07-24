"""NS.Gifts API v2 endpoint enumerations."""

from enum import Enum


class APIEndpoint(str, Enum):
    """Documented NS.Gifts API v2 endpoint paths."""

    GET_TOKEN = "/api/v2/get_token"
    STOCK = "/api/v2/stock"
    CREATE_ORDER = "/api/v2/create_order"
    PAY_ORDER = "/api/v2/pay_order"
    ORDER_INFO = "/api/v2/order_info/{custom_id}"
    EXCHANGE_RATE = "/api/v2/exchange_rate"
    CHECK_BALANCE = "/api/v2/check_balance"
    STEAM_GIFT_APPS = "/api/v2/steam_gift/get_apps"
    STEAM_CHECK_USER = "/api/v2/steam/check_user"
