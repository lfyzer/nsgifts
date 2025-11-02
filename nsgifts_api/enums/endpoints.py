"""API endpoints enumeration."""

from enum import Enum


class BaseEndpoint(str, Enum):
    """Base API endpoints."""
    
    BASE_PATH = "/api/v1"
    PRODUCTS_PATH = "/api/v1/products"
    STEAM_PATH = "/api/v1/steam"
    STEAM_GIFT_PATH = "/api/v1/steam_gift"
    IP_WHITELIST_PATH = "/api/v1/ip-whitelist"

    def __str__(self) -> str:
        return self.value

class UserEndpoint(str, Enum):
    """User-related endpoints."""
    
    LOGIN = f"{BaseEndpoint.BASE_PATH}/get_token"
    SIGNUP = f"{BaseEndpoint.BASE_PATH}/signup"
    CHECK_BALANCE = f"{BaseEndpoint.BASE_PATH}/check_balance"
    GET_USER_INFO = f"{BaseEndpoint.BASE_PATH}/user"


class ServicesEndpoint(str, Enum):
    """Service catalog endpoints."""
    
    GET_ALL_SERVICES = f"{BaseEndpoint.PRODUCTS_PATH}/get_all_services"
    GET_CATEGORIES = f"{BaseEndpoint.PRODUCTS_PATH}/get_categories"
    GET_SERVICES_BY_CATEGORY = f"{BaseEndpoint.PRODUCTS_PATH}/get_services"


class OrdersEndpoint(str, Enum):
    """Order management endpoints."""
    
    CREATE_ORDER = f"{BaseEndpoint.BASE_PATH}/create_order"
    PAY_ORDER = f"{BaseEndpoint.BASE_PATH}/pay_order"
    GET_ORDER_INFO = f"{BaseEndpoint.BASE_PATH}/order_info"


class SteamEndpoint(str, Enum):
    """Steam-related endpoints."""

    CALCULATE_AMOUNT = f"{BaseEndpoint.STEAM_PATH}/get_amount"
    GET_CURRENCY_RATE = f"{BaseEndpoint.STEAM_PATH}/get_currency_rate"
    CALCULATE_GIFT = f"{BaseEndpoint.STEAM_GIFT_PATH}/calculate"
    CREATE_GIFT_ORDER = f"{BaseEndpoint.STEAM_GIFT_PATH}/create_order"
    PAY_GIFT_ORDER = f"{BaseEndpoint.STEAM_GIFT_PATH}/pay_order"
    GET_APPS = f"{BaseEndpoint.STEAM_GIFT_PATH}/get_apps"


class IPWhitelistEndpoint(str, Enum):
    """IP whitelist management endpoints."""

    ADD_IP = f"{BaseEndpoint.IP_WHITELIST_PATH}/add"
    REMOVE_IP = f"{BaseEndpoint.IP_WHITELIST_PATH}/remove"
    LIST_IPS = f"{BaseEndpoint.IP_WHITELIST_PATH}/list"


class Endpoint:
    """Grouped endpoints for easy access."""
    
    USER = UserEndpoint
    SERVICES = ServicesEndpoint
    ORDERS = OrdersEndpoint
    STEAM = SteamEndpoint
    IP_WHITELIST = IPWhitelistEndpoint