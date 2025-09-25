"""Service and category models."""

from typing import List
from pydantic import BaseModel


class CategoryRequest(BaseModel):
    """Request services from specific category.
    
    Attributes:
        category_id: Category ID to filter by.
    """
    
    category_id: int


class ServiceItem(BaseModel):
    """Single service info.
    
    Attributes:
        service_name: Service display name.
        service_id: Unique service ID.
        price: Price in specified currency.
        currency: Price currency (USD, RUB, etc).
        in_stock: How many available.
    """
    
    service_name: str
    service_id: int
    price: float
    currency: str
    in_stock: int


class CategoryItem(BaseModel):
    """Category with its services.
    
    Attributes:
        category_name: Category display name.
        category_id: Unique category ID.
        services: All services in this category.
    """
    
    category_name: str
    category_id: int
    services: List[ServiceItem]


class GetServicesResponseModel(BaseModel):
    """Complete service catalog.
    
    Attributes:
        categories: All categories with their services.
    """
    
    categories: List[CategoryItem]
