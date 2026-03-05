from backend.models import ReadingHistory, ReadingStats, Article
from backend.schemas.reading import ReadingEnd, ReadingHistoryResponse, ReadingStatsResponse
from datetime import datetime
from typing import List

async def start_reading(user_id: int, article_id: int) -> ReadingHistoryResponse:
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")
    history = await ReadingHistory.create(
        user_id=user_id,
        article_id=article_id,
        started_at=datetime.now()
    )
    return ReadingHistoryResponse(
        id=history.id,
        article_id=article.id,
        article_title=article.title,
        started_at=history.started_at,
        ended_at=history.ended_at,
        reading_duration=history.reading_duration,
        reading_progress=history.reading_progress
    )

async def end_reading(user_id: int, article_id: int, data: ReadingEnd) -> ReadingHistoryResponse:
    history = await ReadingHistory.filter(
        user_id=user_id,
        article_id=article_id
    ).order_by("-started_at").first()
    if not history:
        raise ValueError("没有找到阅读记录")
    history.ended_at = datetime.now()
    history.reading_progress = data.reading_progress
    history.reading_duration = int((history.ended_at - history.started_at).total_seconds())
    await history.save()
    stats, created = await ReadingStats.get_or_create(
        user_id=user_id,
        article_id=article_id,
        defaults={
            "total_views": 1,
            "total_duration": history.reading_duration
        }
    )
    if not created:
        stats.total_views += 1
        stats.total_duration += history.reading_duration
        await stats.save()
    article = await Article.get(id=article_id)
    return ReadingHistoryResponse(
        id=history.id,
        article_id=article.id,
        article_title=article.title,
        started_at=history.started_at,
        ended_at=history.ended_at,
        reading_duration=history.reading_duration,
        reading_progress=history.reading_progress
    )

async def get_reading_history(user_id: int, page: int = 1, size: int = 20) -> tuple[List[ReadingHistoryResponse], int]:
    total = await ReadingHistory.filter(user_id=user_id).count()
    histories = await ReadingHistory.filter(
        user_id=user_id
    ).order_by("-started_at").prefetch_related("article").offset((page - 1) * size).limit(size)
    return (
        [
            ReadingHistoryResponse(
                id=h.id,
                article_id=h.article_id,
                article_title=h.article.title,
                started_at=h.started_at,
                ended_at=h.ended_at,
                reading_duration=h.reading_duration,
                reading_progress=h.reading_progress
            ) for h in histories
        ],
        total
    )

async def get_reading_stats(user_id: int, page: int = 1, size: int = 20) -> tuple[List[ReadingStatsResponse], int]:
    total = await ReadingStats.filter(user_id=user_id).count()
    stats = await ReadingStats.filter(
        user_id=user_id
    ).order_by("-last_read_at").prefetch_related("article").offset((page - 1) * size).limit(size)
    return (
        [
            ReadingStatsResponse(
                article_id=s.article_id,
                article_title=s.article.title,
                total_views=s.total_views,
                total_duration=s.total_duration,
                last_read_at=s.last_read_at
            ) for s in stats
        ],
        total
    )

async def get_article_reading_stats(article_id: int, page: int = 1, size: int = 20) -> tuple[List[ReadingStatsResponse], int]:
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")
    total = await ReadingStats.filter(article_id=article_id).count()
    stats = await ReadingStats.filter(
        article_id=article_id
    ).order_by("-total_views").prefetch_related("article", "user").offset((page - 1) * size).limit(size)
    return (
        [
            ReadingStatsResponse(
                article_id=s.article_id,
                article_title=s.article.title,
                total_views=s.total_views,
                total_duration=s.total_duration,
                last_read_at=s.last_read_at
            ) for s in stats
        ],
        total
    )
