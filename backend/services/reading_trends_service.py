from datetime import datetime, timedelta, timezone
from typing import List, Dict
from collections import defaultdict
from backend.models import ReadingHistory

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

    # 获取阅读历史记录
    histories = await ReadingHistory.filter(
        user_id=user_id,
        started_at__gte=start_date
    ).all()

    # 在 Python 中按日期分组
    daily_data = defaultdict(lambda: {'minutes': 0, 'articles': set()})

    for history in histories:
        date_str = history.started_at.strftime('%Y-%m-%d')
        daily_data[date_str]['minutes'] += (history.reading_duration or 0)
        daily_data[date_str]['articles'].add(history.article_id)

    # 转换为目标格式
    date_map = {}
    for date_str, data in daily_data.items():
        date_map[date_str] = {
            'minutes': int(data['minutes'] / 60),  # 转换为分钟
            'articles': len(data['articles'])
        }

    # 填充缺失日期
    result = []
    for i in range(days):
        date = (get_now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
        if date in date_map:
            result.append({
                'date': date,
                'minutes': date_map[date]['minutes'],
                'articles': date_map[date]['articles']
            })
        else:
            result.append({
                'date': date,
                'minutes': 0,
                'articles': 0
            })

    return result
