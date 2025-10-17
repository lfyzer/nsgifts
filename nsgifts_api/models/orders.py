"""Order models for creating and managing orders."""

from typing import Optional

from pydantic import BaseModel


class CreateOrder(BaseModel):
    """Order creation data.
    
    Simple model for creating orders. Just specify what you want and how 
    much.
    
    Attributes:
        service_id (int): Which service to order from the catalog.
        quantity (float): How much you want (depends on service type).
        custom_id (str): Your own ID for tracking this order.
        data (Optional[str]): Extra info like Steam username if needed.
    """
    
    service_id: int
    quantity: float
    custom_id: str
    data: Optional[str] = None