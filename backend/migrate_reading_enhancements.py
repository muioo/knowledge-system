"""
数据库迁移脚本：增强阅读记录功能

运行方式：
    python migrate_reading_enhancements.py

功能：
1. 为 reading_history 表添加新字段和索引
2. 为 reading_stats 表添加新字段和索引
3. 创建 reading_goals 表（阅读目标）
4. 创建 reading_notes 表（阅读笔记）

注意：请先备份数据库再运行此脚本
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tortoise import Tortoise
from backend.settings.config import TORTOISE_ORM
from backend.models import ReadingHistory, ReadingStats


async def migrate():
    """执行数据库迁移"""

    print("=" * 60)
    print("数据库迁移：增强阅读记录功能")
    print("=" * 60)

    # 初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)

    conn = Tortoise.get_connection("default")
    db_client = conn.migration_client

    print("\n[1/5] 为 reading_history 表添加新字段...")

    # 检查字段是否已存在
    columns = await db_client.execute_query("SHOW COLUMNS FROM reading_history")
    existing_columns = {col[0] for col in columns[1]}

    # 添加新字段到 reading_history
    new_history_fields = {
        "session_id": "VARCHAR(100) NULL COMMENT '阅读会话ID，用于关联同一次阅读的多次暂停/继续'",
        "is_completed": "BOOLEAN DEFAULT FALSE COMMENT '是否已完成阅读（进度>=100%）'",
        "device_type": "VARCHAR(50) NULL COMMENT '设备类型（desktop/mobile/tablet）'",
        "ip_address": "VARCHAR(50) NULL COMMENT 'IP地址'",
        "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'",
    }

    for field, definition in new_history_fields.items():
        if field not in existing_columns:
            await db_client.execute_query(f"ALTER TABLE reading_history ADD COLUMN {field} {definition}")
            print(f"  ✓ 添加字段: {field}")
        else:
            print(f"  - 字段已存在，跳过: {field}")

    print("\n[2/5] 为 reading_history 表添加索引...")

    # 检查现有索引
    indexes_result = await db_client.execute_query("SHOW INDEX FROM reading_history")
    existing_indexes = {idx[2] for idx in indexes_result[1]}

    new_history_indexes = [
        ("idx_user_started", "CREATE INDEX idx_user_started ON reading_history(user_id, started_at)"),
        ("idx_user_article", "CREATE INDEX idx_user_article ON reading_history(user_id, article_id)"),
        ("idx_user_article_started", "CREATE INDEX idx_user_article_started ON reading_history(user_id, article_id, started_at)"),
        ("idx_session", "CREATE INDEX idx_session ON reading_history(session_id)"),
    ]

    for idx_name, sql in new_history_indexes:
        if idx_name not in existing_indexes:
            await db_client.execute_query(sql)
            print(f"  ✓ 添加索引: {idx_name}")
        else:
            print(f"  - 索引已存在，跳过: {idx_name}")

    print("\n[3/5] 为 reading_stats 表添加新字段...")

    columns = await db_client.execute_query("SHOW COLUMNS FROM reading_stats")
    existing_columns = {col[0] for col in columns[1]}

    new_stats_fields = {
        "completed_reads": "INT DEFAULT 0 COMMENT '完成阅读次数（进度>=100%）'",
        "avg_duration": "INT DEFAULT 0 COMMENT '平均每次阅读时长（秒）'",
        "last_reading_progress": "INT DEFAULT 0 COMMENT '最后阅读进度（0-100）'",
        "max_reading_progress": "INT DEFAULT 0 COMMENT '最高阅读进度（0-100）'",
        "first_read_at": "DATETIME NULL COMMENT '首次阅读时间'",
    }

    for field, definition in new_stats_fields.items():
        if field not in existing_columns:
            await db_client.execute_query(f"ALTER TABLE reading_stats ADD COLUMN {field} {definition}")
            print(f"  ✓ 添加字段: {field}")
        else:
            print(f"  - 字段已存在，跳过: {field}")

    print("\n[4/5] 为 reading_stats 表添加索引...")

    indexes_result = await db_client.execute_query("SHOW INDEX FROM reading_stats")
    existing_indexes = {idx[2] for idx in indexes_result[1]}

    new_stats_indexes = [
        ("idx_user_last_read", "CREATE INDEX idx_user_last_read ON reading_stats(user_id, last_read_at)"),
        ("idx_user_total_views", "CREATE INDEX idx_user_total_views ON reading_stats(user_id, total_views)"),
        ("idx_user_total_duration", "CREATE INDEX idx_user_total_duration ON reading_stats(user_id, total_duration)"),
    ]

    for idx_name, sql in new_stats_indexes:
        if idx_name not in existing_indexes:
            await db_client.execute_query(sql)
            print(f"  ✓ 添加索引: {idx_name}")
        else:
            print(f"  - 索引已存在，跳过: {idx_name}")

    print("\n[5/5] 创建新表...")

    # 检查表是否已存在
    tables_result = await db_client.execute_query("SHOW TABLES")
    existing_tables = {tbl[0] for tbl in tables_result[1]}

    # 创建 reading_goals 表
    if "reading_goals" not in existing_tables:
        await db_client.execute_query("""
            CREATE TABLE reading_goals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                goal_type VARCHAR(20) NOT NULL COMMENT '目标类型：daily/weekly/monthly',
                target_duration INT NOT NULL COMMENT '目标阅读时长（分钟）',
                target_articles INT DEFAULT 0 COMMENT '目标阅读文章数',
                is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
                start_date DATE NOT NULL COMMENT '目标开始日期',
                end_date DATE NULL COMMENT '目标结束日期',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_active_start (user_id, is_active, start_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='阅读目标表'
        """)
        print("  ✓ 创建表: reading_goals")
    else:
        print("  - 表已存在，跳过: reading_goals")

    # 创建 reading_notes 表
    if "reading_notes" not in existing_tables:
        await db_client.execute_query("""
            CREATE TABLE reading_notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                article_id INT NOT NULL,
                content TEXT NOT NULL COMMENT '笔记内容',
                note_type VARCHAR(20) DEFAULT 'text' COMMENT '笔记类型：text/code/quote',
                chapter_title VARCHAR(200) NULL COMMENT '章节标题',
                section_index INT NULL COMMENT '章节索引',
                reading_progress INT NULL COMMENT '添加笔记时的阅读进度（0-100）',
                color VARCHAR(20) DEFAULT 'yellow' COMMENT '笔记颜色：yellow/blue/green/pink',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
                INDEX idx_user_article (user_id, article_id),
                INDEX idx_user_created (user_id, created_at),
                INDEX idx_article_created (article_id, created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='阅读笔记表'
        """)
        print("  ✓ 创建表: reading_notes")
    else:
        print("  - 表已存在，跳过: reading_notes")

    print("\n" + "=" * 60)
    print("✅ 数据库迁移完成！")
    print("=" * 60)

    # 更新现有数据的 max_reading_progress
    print("\n正在更新现有数据...")
    await db_client.execute_query("""
        UPDATE reading_stats
        SET max_reading_progress = (
            SELECT MAX(reading_progress)
            FROM reading_history
            WHERE reading_history.article_id = reading_stats.article_id
            AND reading_history.user_id = reading_stats.user_id
        )
    """)
    print("  ✓ 已更新 max_reading_progress")

    await Tortoise.close_connections()


if __name__ == '__main__':
    print("\n⚠️  警告：此脚本将修改数据库结构！")
    print("建议先备份数据库。")
    print()

    confirm = input("是否继续？(输入 'yes' 继续): ")
    if confirm.lower() == 'yes':
        asyncio.run(migrate())
    else:
        print("已取消迁移。")
