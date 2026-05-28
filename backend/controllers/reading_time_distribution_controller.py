from datetime import datetime, timezone
from typing import List, Dict
from backend.models import ReadingHistory

def get_now():
    return datetime.now(timezone.utc).astimezone()

async def get_time_distribution(user_id: int) -> Dict:
    """
    获取阅读时段分布数据

    Returns:
    {
        periods: [
            { name: "早晨", count: 12, duration: 360, percentage: 25 }
        ],
        heatmap: [
            { hour: 9, day: 1, count: 5 }
        ]
    }
    """
    histories = await ReadingHistory.filter(user_id=user_id).all()

    # 定义时段
    period_map = {
        "morning": {"name": "早晨", "hours": range(6, 12), "count": 0, "duration": 0},
        "afternoon": {"name": "下午", "hours": range(12, 18), "count": 0, "duration": 0},
        "evening": {"name": "晚上", "hours": range(18, 24), "count": 0, "duration": 0},
        "night": {"name": "深夜", "hours": range(0, 6), "count": 0, "duration": 0},
    }

    # 热力图数据 (24小时 x 7天)
    heatmap = {hour: {day: 0 for day in range(7)} for hour in range(24)}

    total_count = 0
    total_duration = 0

    for h in histories:
        hour = h.started_at.hour
        day = h.started_at.weekday()

        # 统计时段
        for key, period in period_map.items():
            if hour in period["hours"]:
                period["count"] += 1
                period["duration"] += h.reading_duration
                break

        # 统计热力图
        heatmap[hour][day] += 1

        total_count += 1
        total_duration += h.reading_duration

    # 计算百分比并格式化时段数据
    periods = []
    for period in period_map.values():
        percentage = (period["duration"] / total_duration * 100) if total_duration > 0 else 0
        periods.append({
            "name": period["name"],
            "count": period["count"],
            "duration": period["duration"] // 60,  # 转换为分钟
            "percentage": round(percentage, 1)
        })

    # 格式化热力图数据
    heatmap_list = []
    for hour in range(24):
        for day in range(7):
            if heatmap[hour][day] > 0:
                heatmap_list.append({
                    "hour": hour,
                    "day": day,
                    "count": heatmap[hour][day]
                })

    return {
        "periods": periods,
        "heatmap": heatmap_list
    }
