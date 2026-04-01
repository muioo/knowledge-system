"""
生成测试阅读数据脚本

为当前用户创建模拟的阅读记录，用于测试阅读统计功能。
使用方法: 在 backend 目录下运行 python scripts/create_test_reading_data.py
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone

# 切换到 backend 目录
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(backend_dir)

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

from tortoise import Tortoise
from backend.models import User, Article, ReadingHistory, ReadingStats
from backend.settings.config import TORTOISE_ORM


async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(config=TORTOISE_ORM)


def get_now():
    return datetime.now(timezone.utc).astimezone()


async def create_test_reading_data():
    """创建测试阅读数据"""

    # 初始化数据库连接
    await init_db()

    # 获取 admin 用户
    admin_user = await User.get_or_none(username='admin')
    if not admin_user:
        print("错误: 找不到 admin 用户，请先创建用户")
        print("提示: 运行 python create_admin.py 创建管理员用户")
        return

    print(f"为用户 {admin_user.username} (ID: {admin_user.id}) 创建测试阅读数据...")

    # 获取文章
    articles = await Article.all().limit(10)
    if len(articles) < 1:
        print("错误: 数据库中没有文章，请先创建一些文章")
        return

    print(f"找到 {len(articles)} 篇文章")

    # 清除旧的测试数据（可选，取消注释以清除）
    # await ReadingHistory.filter(user_id=admin_user.id).delete()
    # await ReadingStats.filter(user_id=admin_user.id).delete()
    # print("已清除旧的测试数据")

    # 生成过去30天的阅读记录
    now = get_now()
    reading_count = 0

    for days_ago in range(30, 0, -1):
        # 每天随机阅读 1-3 次
        daily_readings = (days_ago % 3) + 1

        for i in range(daily_readings):
            # 选择文章
            article = articles[(days_ago + i) % len(articles)]

            # 随机时间（早上、下午、晚上、深夜）
            hour_choices = [8, 9, 14, 15, 20, 21, 22]
            hour = hour_choices[(days_ago + i) % len(hour_choices)]
            minute = ((days_ago * 7) + i * 5) % 60

            started_at = now - timedelta(
                days=days_ago,
                hours=(now.hour - hour) % 24,
                minutes=(now.minute - minute) % 60
            )

            # 随机阅读时长（5-90分钟）
            duration_minutes = 5 + ((days_ago * 11) + i * 7) % 86
            duration_seconds = duration_minutes * 60

            # 随机阅读进度（10%-100%）
            progress = 10 + ((days_ago * 13) + i * 5) % 91
            if progress > 100:
                progress = 100

            ended_at = started_at + timedelta(seconds=duration_seconds)

            # 创建阅读历史记录
            history = await ReadingHistory.create(
                user_id=admin_user.id,
                article_id=article.id,
                started_at=started_at,
                ended_at=ended_at,
                reading_duration=duration_seconds,
                reading_progress=progress
            )
            reading_count += 1

            # 更新或创建阅读统计
            stats, created = await ReadingStats.get_or_create(
                user_id=admin_user.id,
                article_id=article.id,
                defaults={
                    'total_views': 1,
                    'total_duration': duration_seconds,
                    'last_read_at': ended_at
                }
            )

            if not created:
                stats.total_views += 1
                stats.total_duration += duration_seconds
                stats.last_read_at = ended_at
                await stats.save()

        # 每10天显示进度
        if days_ago % 10 == 0:
            print(f"已生成 {30 - days_ago + 1} 天的数据...")

    print(f"\n[OK] 成功创建 {reading_count} 条阅读记录！")
    print(f"\n数据概览:")
    print(f"- 用户: {admin_user.username}")
    print(f"- 文章数: {len(articles)} 篇")
    print(f"- 阅读记录: {reading_count} 条")
    print(f"- 时间范围: 过去30天")

    # 统计总数据
    total_histories = await ReadingHistory.filter(user_id=admin_user.id).count()
    total_stats = await ReadingStats.filter(user_id=admin_user.id).count()

    print(f"\n数据库中该用户的总数据:")
    print(f"- 阅读历史: {total_histories} 条")
    print(f"- 阅读统计: {total_stats} 篇文章")

    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(create_test_reading_data())
