"""Service and category models."""

from typing import List

from pydantic import BaseModel


class CategoryRequest(BaseModel):
    """Request services from specific category.
    
    Attributes:
        category_id (int): Category ID to filter by.
    """
    
    category_id: int


class ServiceItem(BaseModel):
    """Single service info.
    
    Attributes:
        service_name (str): Service display name.
        service_id (int): Unique service ID.
        price (float): Price in specified currency.
        currency (str): Price currency (USD, RUB, etc).
        in_stock (int): How many available.
    """
    
    service_name: str
    service_id: int
    price: float
    currency: str
    in_stock: int


class CategoryItem(BaseModel):
    """Category with its services.
    
    Attributes:
        category_name (str): Category display name.
        category_id (int): Unique category ID.
        services (List[ServiceItem]): All services in this category.
    """
    
    category_name: str
    category_id: int
    services: List[ServiceItem]


class GetServicesResponseModel(BaseModel):
    """Complete service catalog.
    
    Attributes:
        categories (List[CategoryItem]): All categories with their services.
    """
    
    categories: List[CategoryItem]
