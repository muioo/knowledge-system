"""
手动执行数据库迁移 SQL
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings.config import settings
from tortoise import Tortoise


# 需要添加的字段 (table, column_name, definition)
COLUMNS_TO_ADD = [
    ("reading_history", "is_completed", "TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已完成阅读（进度>=100%）'"),
    ("reading_history", "actual_progress", "INT NOT NULL DEFAULT 0 COMMENT '实际阅读进度（基于滚动位置计算）'"),
    ("reading_history", "device_type", "VARCHAR(50) NULL COMMENT '设备类型（desktop/mobile/tablet）'"),
    ("reading_history", "total_content_length", "INT NOT NULL DEFAULT 0 COMMENT '总内容长度（像素）'"),
    ("reading_history", "scroll_position", "INT NOT NULL DEFAULT 0 COMMENT '滚动位置（像素）'"),
    ("reading_history", "ip_address", "VARCHAR(50) NULL COMMENT 'IP地址'"),
    ("reading_history", "session_id", "VARCHAR(100) NULL COMMENT '阅读会话ID，用于关联同一次阅读的多次暂停/继续'"),
    ("reading_history", "created_at", "DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'"),
    ("reading_stats", "max_reading_progress", "INT NOT NULL DEFAULT 0 COMMENT '最高阅读进度（0-100）'"),
    ("reading_stats", "avg_duration", "INT NOT NULL DEFAULT 0 COMMENT '平均每次阅读时长（秒）'"),
    ("reading_stats", "completed_reads", "INT NOT NULL DEFAULT 0 COMMENT '完成阅读次数（进度>=100%）'"),
    ("reading_stats", "first_read_at", "DATETIME(6) NULL COMMENT '首次阅读时间'"),
    ("reading_stats", "last_reading_progress", "INT NOT NULL DEFAULT 0 COMMENT '最后阅读进度（0-100）'"),
]

# 需要添加的索引 (table, index_name, index_definition)
INDEXES_TO_ADD = [
    ("reading_history", "idx_reading_his_user_id_a8491b", "(`user_id`, `article_id`, `started_at`)"),
    ("reading_history", "idx_reading_his_session_21785c", "(`session_id`)"),
    ("reading_history", "idx_reading_his_user_id_2c4563", "(`user_id`, `started_at`)"),
    ("reading_history", "idx_reading_his_user_id_9d0e56", "(`user_id`, `article_id`)"),
    ("reading_stats", "idx_reading_sta_user_id_d78b8b", "(`user_id`, `last_read_at`)"),
    ("reading_stats", "idx_reading_sta_user_id_b95026", "(`user_id`, `total_duration`)"),
    ("reading_stats", "idx_reading_sta_user_id_5e2dac", "(`user_id`, `total_views`)"),
]

# 需要创建的表
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS `reading_goals` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `goal_type` VARCHAR(20) NOT NULL COMMENT 'goal type',
    `target_duration` INT NOT NULL COMMENT 'target reading duration (minutes)',
    `target_articles` INT NOT NULL DEFAULT 0 COMMENT 'target article count',
    `is_active` BOOL NOT NULL DEFAULT 1 COMMENT 'is active',
    `start_date` DATE NOT NULL COMMENT 'start date',
    `end_date` DATE NULL COMMENT 'end date',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_reading__users_0bc5bbe2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_reading_goa_user_id_c76634` (`user_id`, `is_active`, `start_date`)
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS `reading_notes` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `content` LONGTEXT NOT NULL COMMENT 'note content',
    `note_type` VARCHAR(20) NOT NULL DEFAULT 'text' COMMENT 'note type',
    `chapter_title` VARCHAR(200) NULL COMMENT 'chapter title',
    `section_index` INT NULL COMMENT 'section index',
    `reading_progress` INT NULL COMMENT 'reading progress when note added',
    `color` VARCHAR(20) NOT NULL DEFAULT 'yellow' COMMENT 'note color',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `article_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_reading__articles_5cb68475` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reading__users_82df4220` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_reading_not_user_id_c8a00c` (`user_id`, `article_id`),
    KEY `idx_reading_not_user_id_136a09` (`user_id`, `created_at`),
    KEY `idx_reading_not_article_dda356` (`article_id`, `created_at`)
) CHARACTER SET utf8mb4;
"""


async def column_exists(conn, table: str, column: str) -> bool:
    """检查列是否存在"""
    result = await conn.execute_query(
        f"SHOW COLUMNS FROM `{table}` LIKE '{column}'"
    )
    return len(result[1]) > 0


async def index_exists(conn, table: str, index: str) -> bool:
    """检查索引是否存在"""
    result = await conn.execute_query(
        f"SHOW INDEX FROM `{table}` WHERE Key_name = '{index}'"
    )
    return len(result[1]) > 0


async def run_migration():
    """执行迁移"""
    await Tortoise.init(config=settings.tortoise_orm)
    conn = Tortoise.get_connection("default")

    print("Starting database migration...")

    # 添加列
    for table, column, definition in COLUMNS_TO_ADD:
        try:
            exists = await column_exists(conn, table, column)
            if exists:
                print(f"  Column {table}.{column} already exists, skipping")
            else:
                sql = f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"
                print(f"  Adding column {table}.{column}...")
                await conn.execute_query(sql)
                print(f"    Done!")
        except Exception as e:
            print(f"    Error: {e}")

    # 添加索引
    for table, index, definition in INDEXES_TO_ADD:
        try:
            exists = await index_exists(conn, table, index)
            if exists:
                print(f"  Index {table}.{index} already exists, skipping")
            else:
                sql = f"ALTER TABLE `{table}` ADD INDEX `{index}` {definition}"
                print(f"  Adding index {table}.{index}...")
                await conn.execute_query(sql)
                print(f"    Done!")
        except Exception as e:
            print(f"    Error: {e}")

    # 创建表
    statements = [s.strip() for s in CREATE_TABLES_SQL.split(';') if s.strip()]
    for stmt in statements:
        try:
            print(f"  Creating table...")
            await conn.execute_query(stmt)
            print(f"    Done!")
        except Exception as e:
            error_msg = str(e).lower()
            if 'already exists' in error_msg:
                print(f"    Already exists, skipping")
            else:
                print(f"    Error: {e}")

    await Tortoise.close_connections()
    print("\nMigration complete!")


if __name__ == "__main__":
    asyncio.run(run_migration())
