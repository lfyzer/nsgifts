"""Order API request models."""

from typing import Optional

from pydantic import BaseModel, Field


class CreateOrder(BaseModel):
    """Order creation request.
    
    Simple model for creating orders. Just specify what you want and how 
    much.
    
    Attributes:
        service_id (int): Which service to order from the catalog.
        quantity (float): How much you want (depends on service type).
        custom_id (str): Your own ID for tracking this order.
        data (Optional[str]): Extra info like Steam username if needed.
    """
    
    service_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    custom_id: str = Field(..., min_length=1, max_length=255)
    data: Optional[str] = Field(None, max_length=1000)


class PayOrder(BaseModel):
    """Payment request.
    
    Attributes:
        custom_id (str): Order ID to pay for.
    """
    
    custom_id: str = Field(..., min_length=1, max_length=255)