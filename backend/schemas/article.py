from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    source_url: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None

class ArticleCreate(ArticleBase):
    tag_ids: Optional[List[int]] = []

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    source_url: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None
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


class ArticleFromHtmlUrlRequest(BaseModel):
    """从 HTML URL 导入文章请求"""
    url: str = Field(..., min_length=1, max_length=1000)
    tag_ids: Optional[List[int]] = []


class ArticleFromHtmlUrlResponse(BaseModel):
    """从 HTML URL 导入文章响应"""
    article_id: int
    status: str  # pending
    message: str


class ArticleHtmlResponse(ArticleResponse):
    """包含 HTML 内容的文章响应"""
    html_content: Optional[str] = None
    html_path: Optional[str] = None
    processing_status: Optional[str] = None
