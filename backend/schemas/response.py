from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class SuccessResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T

class PaginatedResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: "PaginatedData[T]"

class PaginatedData(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    items: list[T]

class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: Optional[dict] = None
