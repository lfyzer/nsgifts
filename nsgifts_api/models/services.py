"""Service and category models."""

from pydantic import BaseModel


class CategoryRequest(BaseModel):
    """Request services from specific category.
    
    Attributes:
        category_id (int): Category ID to filter by.
    """
    
    category_id: int