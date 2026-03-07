"""
添加 reading_progress 字段到 reading_history 表
"""
import pymysql
import sys


def add_reading_progress_column():
    """添加 reading_progress 列到 reading_history 表"""

    # 数据库配置
    db_config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',  # 请根据实际情况修改
        'database': 'knowledge_system',  # 请根据实际情况修改
        'charset': 'utf8mb4'
    }

    try:
        # 连接数据库
        print("正在连接数据库...")
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        print("✓ 数据库连接成功")

        # 检查字段是否已存在
        cursor.execute(
            "SHOW COLUMNS FROM reading_history LIKE 'reading_progress'"
        )
        result = cursor.fetchone()

        if result:
            print("✓ reading_progress 字段已存在，无需添加")
            return

        # 添加字段
        print("正在添加 reading_progress 字段...")
        cursor.execute(
            "ALTER TABLE reading_history ADD COLUMN reading_progress INT DEFAULT 0"
        )
        conn.commit()
        print("✓ 成功添加 reading_progress 字段到 reading_history 表")

    except pymysql.Error as e:
        print(f"✗ 数据库操作失败: {e}")
        print("\n请确认:")
        print("1. MySQL 服务正在运行")
        print("2. 数据库配置正确 (host, port, user, password, database)")
        print("3. 数据库存在 reading_history 表")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("数据库迁移工具")
    print("添加 reading_progress 字段")
    print("=" * 50)
    add_reading_progress_column()
    print("=" * 50)
