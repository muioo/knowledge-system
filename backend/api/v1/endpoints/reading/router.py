from fastapi import APIRouter, HTTPException, Depends
from backend.core.security import get_current_user, get_current_admin
from backend.models import User
from backend.schemas.reading import ReadingEnd, ReadingHistoryResponse, ReadingStatsResponse, ReadingTrendsResponse
from backend.schemas.response import SuccessResponse, PaginatedResponse, PaginatedData
from backend.controllers.reading_controller import (
    start_reading,
    end_reading,
    get_reading_history,
    get_reading_stats,
    get_article_reading_stats
)
from backend.controllers.reading_trends_controller import get_reading_trends
from backend.controllers.reading_time_distribution_controller import get_time_distribution

router = APIRouter(prefix="/reading", tags=["阅读记录"])

@router.post("/articles/{article_id}/start", response_model=SuccessResponse[ReadingHistoryResponse])
async def start_reading_article(
    article_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await start_reading(current_user.id, article_id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/articles/{article_id}/end", response_model=SuccessResponse[ReadingHistoryResponse])
async def end_reading_article(
    article_id: int,
    data: ReadingEnd,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await end_reading(current_user.id, article_id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history", response_model=PaginatedResponse[ReadingHistoryResponse])
async def get_my_reading_history(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    histories, total = await get_reading_history(current_user.id, page, size)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=histories
    ))

@router.get("/stats", response_model=PaginatedResponse[ReadingStatsResponse])
async def get_my_reading_stats(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    stats, total = await get_reading_stats(current_user.id, page, size)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=stats
    ))

@router.get("/articles/{article_id}/stats", response_model=PaginatedResponse[ReadingStatsResponse])
async def get_article_stats(
    article_id: int,
    page: int = 1,
    size: int = 20,
    current_admin: User = Depends(get_current_admin)
):
    try:
        stats, total = await get_article_reading_stats(article_id, page, size)
        return PaginatedResponse(data=PaginatedData(
            total=total,
            page=page,
            size=size,
            items=stats
        ))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/trends", response_model=SuccessResponse[ReadingTrendsResponse])
async def get_trends(
    days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """获取阅读趋势数据"""
    if days not in [7, 30, 90]:
        raise HTTPException(status_code=400, detail="days must be 7, 30, or 90")

    data = await get_reading_trends(current_user.id, days)
    return SuccessResponse(data=ReadingTrendsResponse(
        items=data,
        total=len(data)
    ))

@router.get("/time-distribution")
async def get_distribution(
    current_user: User = Depends(get_current_user)
):
    """获取阅读时段分布数据"""
    data = await get_time_distribution(current_user.id)
    return data
