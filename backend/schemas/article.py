from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str

class ArticleCreate(ArticleBase):
    tag_ids: Optional[List[int]] = []

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class TagInfo(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True

class ArticleResponse(ArticleBase):
    id: int
    author_id: int
    original_filename: Optional[str] = None
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInfo] = []

    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    q: Optional[str] = None
    tags: Optional[List[int]] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
