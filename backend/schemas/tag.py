from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """标签请求和响应共用字段。"""

    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#3498db", pattern=r"^#[0-9A-Fa-f]{6}$")


class TagCreate(TagBase):
    """创建标签请求。"""

    parent_id: Optional[int] = Field(default=None, description="父标签 ID，空值表示顶级标签")


class TagUpdate(BaseModel):
    """更新标签请求。"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    parent_id: Optional[int] = Field(default=None, description="父标签 ID，空值表示顶级标签")


class TagResponse(TagBase):
    """标签响应，携带父级关系和直接关联文章数量。"""

    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    article_count: int = Field(default=0, description="直接关联的文章数量")

    class Config:
        from_attributes = True
