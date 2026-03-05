from pydantic import BaseModel, Field
from datetime import datetime

class ReadingEnd(BaseModel):
    reading_progress: int = Field(default=0, ge=0, le=100)

class ReadingHistoryResponse(BaseModel):
    id: int
    article_id: int
    article_title: str
    started_at: datetime
    ended_at: datetime = None
    reading_duration: int
    reading_progress: int

class ReadingStatsResponse(BaseModel):
    article_id: int
    article_title: str
    total_views: int
    total_duration: int
    last_read_at: datetime
