import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tortoise import Tortoise
from backend.settings.config import TORTOISE_ORM
from backend.models import ReadingHistory, ReadingStats, Article, User
from datetime import datetime, timezone, timedelta

def get_now():
    return datetime.now(timezone.utc).astimezone()

async def check_and_create_data():
    await Tortoise.init(config=TORTOISE_ORM)

    # Check counts
    history_count = await ReadingHistory.all().count()
    stats_count = await ReadingStats.all().count()
    user_count = await User.all().count()
    article_count = await Article.all().count()

    print(f"Users: {user_count}")
    print(f"Articles: {article_count}")
    print(f"Reading history records: {history_count}")
    print(f"Reading stats records: {stats_count}")

    # Update existing records with proper progress values
    if history_count > 0:
        print("\nUpdating existing records with proper progress values...")

        histories = await ReadingHistory.all()
        for i, h in enumerate(histories):
            # Set realistic values
            progress = min(100, 15 + i * 12)
            duration = 180 + i * 90  # 3-20 minutes

            h.actual_progress = progress
            h.reading_progress = progress
            h.reading_duration = duration
            h.scroll_position = progress * 10
            h.total_content_length = 1000
            await h.save()

        print(f"  Updated {len(histories)} history records")

        # Recreate stats with proper values
        await ReadingStats.all().delete()

        histories = await ReadingHistory.all().prefetch_related('article')
        for history in histories:
            stats, created = await ReadingStats.get_or_create(
                user_id=history.user_id,
                article_id=history.article_id,
                defaults={
                    "total_views": 1,
                    "total_duration": history.reading_duration,
                    "last_read_at": history.started_at,
                    "last_reading_progress": history.actual_progress,
                    "max_reading_progress": history.actual_progress
                }
            )

            if not created:
                stats.total_views += 1
                stats.total_duration += history.reading_duration
                stats.last_read_at = history.started_at
                if history.actual_progress > stats.max_reading_progress:
                    stats.max_reading_progress = history.actual_progress
                stats.last_reading_progress = history.actual_progress
                await stats.save()

        print(f"  Recreated reading stats")

    # Show sample history records
    print("\nSample reading history records:")
    histories = await ReadingHistory.all().limit(5).order_by('-started_at')
    for h in histories:
        article = await h.article
        print(f"  - {article.title[:40] if article else 'Unknown'}: progress={h.actual_progress}%, duration={h.reading_duration}s")

    await Tortoise.close_connections()

if __name__ == '__main__':
    asyncio.run(check_and_create_data())
