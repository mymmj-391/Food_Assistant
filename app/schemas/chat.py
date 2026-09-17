from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    session_id: Optional[str] = None


class SourceInfo(BaseModel):
    source: str = Field(..., description="知识来源文件路径")
    category: str = Field(..., description="知识分类")
    type: str = Field(..., description="知识类型（菜品/技巧）")
    text: str = Field(..., description="知识内容摘要")
    distance: float = Field(..., description="相似度距离")


class DishLink(BaseModel):
    name: str = Field(..., description="菜品名称")
    category: str = Field(..., description="菜品分类")
    url: str = Field(..., description="跳转链接")


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[SourceInfo] = []
    dish_links: List[DishLink] = []
