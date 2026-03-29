"""
数据库迁移脚本：添加基于滚动的阅读进度跟踪

运行方式：
    python migrate_scroll_progress.py

功能：
1. 为 reading_history 表添加滚动位置字段
2. 添加实际阅读进度字段
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tortoise import Tortoise
from backend.settings.config import TORTOISE_ORM


async def migrate():
    """执行数据库迁移"""

    print("=" * 60)
    print("数据库迁移：添加滚动位置跟踪")
    print("=" * 60)

    # 初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)

    conn = Tortoise.get_connection("default")
    db_client = conn.migration_client

    print("\n检查现有字段...")

    # 检查字段是否已存在
    columns = await db_client.execute_query("SHOW COLUMNS FROM reading_history")
    existing_columns = {col[0] for col in columns[1]}

    print(f"现有字段: {existing_columns}")

    # 需要添加的字段
    new_fields = {
        "scroll_position": "INT DEFAULT 0 COMMENT '滚动位置（像素）'",
        "total_content_length": "INT DEFAULT 0 COMMENT '总内容长度（像素）'",
        "actual_progress": "INT DEFAULT 0 COMMENT '实际阅读进度（基于滚动位置计算）'",
    }

    for field, definition in new_fields.items():
        if field not in existing_columns:
            await db_client.execute_query(f"ALTER TABLE reading_history ADD COLUMN {field} {definition}")
            print(f"  ✓ 添加字段: {field}")
        else:
            print(f"  - 字段已存在，跳过: {field}")

    print("\n" + "=" * 60)
    print("✅ 数据库迁移完成！")
    print("=" * 60)

    await Tortoise.close_connections()


if __name__ == '__main__':
    print("\n⚠️  此脚本将修改数据库结构！")
    print()

    confirm = input("是否继续？(输入 'yes' 继续): ")
    if confirm.lower() == 'yes':
        asyncio.run(migrate())
    else:
        print("已取消迁移。")
