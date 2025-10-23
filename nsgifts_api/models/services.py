from pydantic import BaseModel, Field


class CategoryRequest(BaseModel):
    category_id: int = Field(..., gt=0)