
from backend.models import ReadingHistory, ReadingStats, Article
from backend.schemas.reading import ReadingEnd, ReadingHistoryResponse, ReadingStatsResponse, ReadingProgressUpdate
from datetime import datetime, timezone
from typing import List, Dict

# 获取当前时间（带时区）
def get_now():
    return datetime.now(timezone.utc).astimezone()

async def start_reading(user_id: int, article_id: int) -> ReadingHistoryResponse:
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")
    history = await ReadingHistory.create(
        user_id=user_id,
        article_id=article_id,
        started_at=get_now()
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
    history.ended_at = get_now()
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
                reading_progress=h.actual_progress,  # 使用 actual_progress
                scroll_position=h.scroll_position,
                actual_progress=h.actual_progress
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
                last_read_at=s.last_read_at,
                max_reading_progress=s.max_reading_progress
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

async def get_reading_progress(user_id: int, page: int = 1, size: int = 20) -> tuple[List[Dict], int]:
    """
    获取文章阅读进度详情

    Returns:
        ([{
            article_id: 1,
            article_title: "...",
            total_views: 3,
            total_duration: 2700,
            reading_progress: 75,
            last_read_at: "2026-03-29T10:00:00Z"
        }], total)
    """
    if page < 1 or size < 1 or size > 100:
        raise ValueError("page must be >= 1 and size must be between 1 and 100")

    total = await ReadingStats.filter(user_id=user_id).count()

    # 获取阅读统计，按最后阅读时间排序
    stats = await ReadingStats.filter(
        user_id=user_id
    ).order_by("-last_read_at").prefetch_related("article").offset((page - 1) * size).limit(size)

    # 批量获取所有相关文章的最新阅读记录，避免N+1查询
    article_ids = [s.article_id for s in stats]

    # 获取每个文章的最新阅读记录（使用单次查询）
    latest_histories = {}
    if article_ids:
        histories = await ReadingHistory.filter(
            user_id=user_id,
            article_id__in=article_ids
        ).order_by("-started_at")

        # 按文章ID分组，取每个文章的最新记录
        for history in histories:
            if history.article_id not in latest_histories:
                latest_histories[history.article_id] = history

    # 构建结果
    result = []
    for s in stats:
        latest_history = latest_histories.get(s.article_id)
        progress = latest_history.reading_progress if latest_history else 0

        result.append({
            "article_id": s.article_id,
            "article_title": s.article.title,
            "total_views": s.total_views,
            "total_duration": s.total_duration,
            "reading_progress": progress,
            "last_read_at": s.last_read_at.isoformat() if s.last_read_at else None
        })

    return result, total


async def update_reading_progress(user_id: int, article_id: int, data: ReadingProgressUpdate) -> Dict:
    """
    更新阅读进度（基于滚动位置）

    Args:
        user_id: 用户ID
        article_id: 文章ID
        data: 进度更新数据

    Returns:
        更新后的阅读进度
    """
    # 获取当前活动的阅读记录
    history = await ReadingHistory.filter(
        user_id=user_id,
        article_id=article_id,
        ended_at=None  # 只更新未结束的记录
    ).order_by("-started_at").first()

    if not history:
        # 如果没有活动记录，创建一个新的
        history = await ReadingHistory.create(
            user_id=user_id,
            article_id=article_id,
            started_at=get_now(),
            scroll_position=data.scroll_position,
            total_content_length=data.total_content_length,
            actual_progress=data.actual_progress
        )
    else:
        # 更新现有记录
        history.scroll_position = data.scroll_position
        history.total_content_length = data.total_content_length
        history.actual_progress = data.actual_progress
        history.reading_progress = data.actual_progress  # 同步更新进度
        await history.save()

    # 更新阅读统计
    stats, created = await ReadingStats.get_or_create(
        user_id=user_id,
        article_id=article_id,
        defaults={
            "total_views": 1,
            "total_duration": 0,
            "last_reading_progress": data.actual_progress,
            "max_reading_progress": data.actual_progress
        }
    )

    if not created:
        # 更新最高进度
        if data.actual_progress > stats.max_reading_progress:
            stats.max_reading_progress = data.actual_progress
        stats.last_reading_progress = data.actual_progress
        await stats.save()

    return {
        "scroll_position": history.scroll_position,
        "total_content_length": history.total_content_length,
        "actual_progress": history.actual_progress,
        "reading_progress": history.reading_progress
    }
