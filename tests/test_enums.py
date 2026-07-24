"""Tests for API v2 enumerations."""

from pathlib import Path

from nsgifts_api.enums import (
    APIEndpoint,
    HTTPMethod,
    OrderStatus,
    PaymentStatus,
    Region,
    StockFieldType,
)


def test_endpoint_values_match_api_v2_documentation() -> None:
    """Verify all documented endpoint paths."""
    assert APIEndpoint.GET_TOKEN == "/api/v2/get_token"
    assert APIEndpoint.STOCK == "/api/v2/stock"
    assert APIEndpoint.CREATE_ORDER == "/api/v2/create_order"
    assert APIEndpoint.PAY_ORDER == "/api/v2/pay_order"
    assert APIEndpoint.ORDER_INFO == ("/api/v2/order_info/{custom_id}")
    assert APIEndpoint.EXCHANGE_RATE == "/api/v2/exchange_rate"
    assert APIEndpoint.CHECK_BALANCE == "/api/v2/check_balance"
    assert APIEndpoint.STEAM_GIFT_APPS == ("/api/v2/steam_gift/get_apps")
    assert APIEndpoint.STEAM_CHECK_USER == ("/api/v2/steam/check_user")


def test_http_methods_include_get_and_post() -> None:
    """Verify the HTTP methods required by API v2."""
    assert HTTPMethod.GET == "GET"
    assert HTTPMethod.POST == "POST"


def test_regions_include_new_v2_regions() -> None:
    """Verify all Steam regions documented by API v2."""
    assert {region.value for region in Region} == {
        "ru",
        "kz",
        "ua",
        "cis",
        "cn",
    }


def test_status_and_field_type_values() -> None:
    """Verify status and dynamic field enum values."""
    assert PaymentStatus.IN_PROGRESS == "in_progress"
    assert OrderStatus.IN_PROGRESS == 10
    assert OrderStatus.REFUNDED == 7
    assert StockFieldType.INTEGER == "int"
    assert StockFieldType.NUMBER == "float"


def test_package_contains_no_api_v1_paths() -> None:
    """Verify the breaking release has no hidden v1 compatibility."""
    package = Path(__file__).parents[1] / "nsgifts_api"
    offenders = [
        path
        for path in package.rglob("*.py")
        if "/api/v1" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []
