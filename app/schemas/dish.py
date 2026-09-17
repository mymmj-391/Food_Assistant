from pydantic import BaseModel
from typing import List, Optional


class DishSummary(BaseModel):
    id: str
    name: str
    summary: str = ""
    type: str = "folder"
    image: Optional[str] = None


class DishListResponse(BaseModel):
    list: List[DishSummary]


class DishDetailResponse(BaseModel):
    name: str
    content: str


class DishImageResponse(BaseModel):
    images: List[str]
