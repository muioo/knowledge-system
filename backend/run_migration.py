"""Quick migration runner - bypasses confirmation prompt"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tortoise import Tortoise
from backend.settings.config import TORTOISE_ORM


async def migrate():
    await Tortoise.init(config=TORTOISE_ORM)
    conn = Tortoise.get_connection("default")

    print("Migrating reading_history table...")

    columns_result = await conn.execute_query("SHOW COLUMNS FROM reading_history")
    # execute_query returns (sql, rows) tuple
    rows = columns_result[1] if isinstance(columns_result, tuple) else columns_result
    existing_columns = {col["Field"] if isinstance(col, dict) else col[0] for col in rows}

    new_fields = {
        "session_id": "VARCHAR(100) NULL COMMENT 'Reading session ID'",
        "is_completed": "BOOLEAN DEFAULT FALSE",
        "device_type": "VARCHAR(50) NULL COMMENT 'Device type'",
        "ip_address": "VARCHAR(50) NULL COMMENT 'IP address'",
        "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "scroll_position": "INT DEFAULT 0 COMMENT 'Scroll position in pixels'",
        "total_content_length": "INT DEFAULT 0 COMMENT 'Total content length in pixels'",
        "actual_progress": "INT DEFAULT 0 COMMENT 'Actual reading progress (0-100)'",
    }

    for field, definition in new_fields.items():
        if field not in existing_columns:
            await conn.execute_query(f"ALTER TABLE reading_history ADD COLUMN {field} {definition}")
            print(f"  Added field: {field}")
        else:
            print(f"  Skipped existing field: {field}")

    print("\nMigrating reading_stats table...")

    columns_result = await conn.execute_query("SHOW COLUMNS FROM reading_stats")
    rows = columns_result[1] if isinstance(columns_result, tuple) else columns_result
    existing_columns = {col["Field"] if isinstance(col, dict) else col[0] for col in rows}

    new_stats_fields = {
        "completed_reads": "INT DEFAULT 0",
        "avg_duration": "INT DEFAULT 0",
        "last_reading_progress": "INT DEFAULT 0",
        "max_reading_progress": "INT DEFAULT 0",
        "first_read_at": "DATETIME NULL",
    }

    for field, definition in new_stats_fields.items():
        if field not in existing_columns:
            await conn.execute_query(f"ALTER TABLE reading_stats ADD COLUMN {field} {definition}")
            print(f"  Added field: {field}")
        else:
            print(f"  Skipped existing field: {field}")

    print("\nMigration completed!")
    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(migrate())
