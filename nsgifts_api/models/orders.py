"""Order models for creating and managing orders."""

from typing import Optional
from pydantic import BaseModel


class CreateOrder(BaseModel):
    """Order creation data.
    
    Simple model for creating orders. Just specify what you want and how 
    much.
    
    Attributes:
        service_id: Which service to order from the catalog.
        quantity: How much you want (can be fractional like 1.5).
        custom_id: Your own ID for tracking this order.
        data: Extra info like Steam username if needed.
    """
    
    service_id: int
    quantity: float
    custom_id: str
    data: Optional[str] = None
