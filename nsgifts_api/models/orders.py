from typing import Optional
from pydantic import BaseModel, Field


class CreateOrder(BaseModel):
    service_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    custom_id: str = Field(..., min_length=1, max_length=255)
    data: Optional[str] = Field(None, max_length=1000)