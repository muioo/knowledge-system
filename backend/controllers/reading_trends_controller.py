from datetime import datetime, timedelta, timezone
from typing import List, Dict
from backend.models import ReadingHistory
from tortoise import functions

def get_now():
    return datetime.now(timezone.utc).astimezone()

async def get_reading_trends(user_id: int, days: int = 7) -> List[Dict]:
    """
    获取阅读趋势数据

    Args:
        user_id: 用户ID
        days: 天数 (7, 30, 90)

    Returns:
        [{ date: "2026-03-29", minutes: 45, articles: 3 }]
    """
    start_date = get_now() - timedelta(days=days)

    # 从阅读历史聚合数据
    histories = await ReadingHistory.filter(
        user_id=user_id,
        started_at__gte=start_date
    ).annotate(
        date=functions.TruncDate('started_at')
    ).group_by('date').values(
        'date',
        minutes=functions.Sum('reading_duration') / 60,
        articles=functions.Count('article_id', distinct=True)
    )

    # 填充缺失日期
    result = []
    date_map = {h['date'].strftime('%Y-%m-%d'): h for h in histories}

    for i in range(days):
        date = (get_now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
        if date in date_map:
            result.append({
                'date': date,
                'minutes': int(date_map[date]['minutes'] or 0),
                'articles': date_map[date]['articles']
            })
        else:
            result.append({
                'date': date,
                'minutes': 0,
                'articles': 0
            })

    return result
