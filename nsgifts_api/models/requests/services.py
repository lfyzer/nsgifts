"""Service API request models."""

from pydantic import BaseModel, Field


class CategoryRequest(BaseModel):
    """Request services from specific category.
    
    Attributes:
        category_id (int): Category ID to filter by.
    """
    
    category_id: int = Field(..., gt=0)