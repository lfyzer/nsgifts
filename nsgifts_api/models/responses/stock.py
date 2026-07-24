"""Stock catalog response models."""

from decimal import Decimal

from pydantic import Field, field_validator

from ...enums import StockFieldType
from ..requests import JSONScalar
from .base import ResponseModel


class StockFieldSchema(ResponseModel):
    """Dynamic order-field schema for one category."""

    key: str
    type: StockFieldType | str
    name: str
    required: bool
    minimum: Decimal | None = Field(default=None, alias="min")
    maximum: Decimal | None = Field(default=None, alias="max")
    step: Decimal | None = None
    regex: str | None = None
    options: list[JSONScalar] | None = Field(
        default=None,
        alias="enum",
    )

    @field_validator("type", mode="before")
    @classmethod
    def parse_known_type(
        cls,
        value: object,
    ) -> StockFieldType | str:
        """Use enums for known types and preserve future strings."""
        try:
            return StockFieldType(str(value))
        except ValueError:
            return str(value)


class StockService(ResponseModel):
    """One service available to the current partner."""

    service_id: int
    service_name: str
    price: Decimal
    currency: str
    in_stock: int


class StockCategory(ResponseModel):
    """A service category and its dynamic order schema."""

    category_name: str
    category_id: int
    services: list[StockService]
    fields: list[StockFieldSchema]


class StockResponse(ResponseModel):
    """Complete partner-specific stock catalog."""

    categories: list[StockCategory]
