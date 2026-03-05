from pydantic import BaseModel, Field
from datetime import datetime

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#3498db", pattern=r"^#[0-9A-Fa-f]{6}$")

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: str = Field(None, min_length=1, max_length=50)
    color: str = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

class TagResponse(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
