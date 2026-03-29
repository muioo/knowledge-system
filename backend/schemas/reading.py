from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ReadingEnd(BaseModel):
    reading_progress: int = Field(default=0, ge=0, le=100)

class ReadingProgressUpdate(BaseModel):
    """阅读进度更新请求"""
    scroll_position: int = Field(default=0, ge=0, description="滚动位置（像素）")
    total_content_length: int = Field(default=0, ge=0, description="总内容长度（像素）")
    actual_progress: int = Field(default=0, ge=0, le=100, description="实际阅读进度（0-100）")

class ReadingTrendItem(BaseModel):
    date: str
    minutes: int
    articles: int

class ReadingTrendsResponse(BaseModel):
    items: List[ReadingTrendItem]
    total: int

class ReadingHistoryResponse(BaseModel):
    id: int
    article_id: int
    article_title: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    reading_duration: int
    reading_progress: int
    scroll_position: int = 0
    actual_progress: int = 0

class ReadingStatsResponse(BaseModel):
    article_id: int
    article_title: str
    total_views: int
    total_duration: int
    last_read_at: Optional[datetime] = None
    max_reading_progress: int = 0