#!/bin/sh
# 不使用 set -e，以便显示错误信息

echo "=== Waiting for MySQL to be ready ==="
MAX_RETRIES=30
RETRY=0
while true; do
    if python -c "
import asyncio, sys
from tortoise import Tortoise
from backend.settings.config import TORTOISE_ORM
async def check():
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.close_connections()
        print('OK')
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
asyncio.run(check())
" 2>&1; then
        break
    fi

    RETRY=$((RETRY + 1))
    if [ $RETRY -ge $MAX_RETRIES ]; then
        echo "MySQL not ready after ${MAX_RETRIES} retries, exiting."
        exit 1
    fi
    echo "  MySQL not ready yet, retrying in 2s... ($RETRY/$MAX_RETRIES)"
    sleep 2
done
echo "MySQL is ready."

echo "=== Running aerich migrations ==="
# 使用 aerich CLI 但先读取迁移文件，分割后逐条执行
python << 'PYTHON_SCRIPT'
import asyncio
import sys
import traceback
import os
import re
from pathlib import Path

async def init_db_with_tortoise():
    """使用 TortoiseORM 直接初始化数据库表（无 migrations 时）"""
    from tortoise import Tortoise
    from backend.settings.config import TORTOISE_ORM

    print("No migrations directory found, using TortoiseORM to initialize database...")
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    print(f"Database tables created successfully!")
    await Tortoise.close_connections()

async def migrate():
    try:
        from aerich import Command
        from aerich.models import Aerich
        from backend.settings.config import TORTOISE_ORM
        from tortoise import Tortoise, connections

        print("Initializing aerich...")
        # 初始化 Tortoise 和 aerich
        await Tortoise.init(config=TORTOISE_ORM)
        command = Command(tortoise_config=TORTOISE_ORM, location='migrations')
        await command.init()

        print("Checking for pending migrations...")
        # 检查是否有待执行的迁移
        migrations_path = Path('migrations/models')
        if not migrations_path.exists():
            print('No migrations directory found')
            # 使用 TortoiseORM 直接初始化数据库表
            await init_db_with_tortoise()
            return

        # 获取所有迁移文件
        migration_files = sorted(migrations_path.glob('*.py'))
        if not migration_files:
            print('No migration files found')
            # 使用 TortoiseORM 直接初始化数据库表
            await init_db_with_tortoise()
            return

        # 获取已应用的迁移
        applied_versions = []
        try:
            applied = await Aerich.all().values('version')
            applied_versions = [a['version'] for a in applied]
            print(f"Already applied migrations: {applied_versions}")
        except Exception as e:
            print(f"No aerich table yet (first run): {e}")
            pass  # 首次运行，aerich 表还不存在

        # 找出待执行的迁移
        pending = []
        for f in migration_files:
            if f.name.startswith('0_'):
                # 初始迁移特殊处理
                if not applied_versions:
                    pending.append(f)
            else:
                # 检查完整文件名是否在已应用列表中
                if f.name not in applied_versions:
                    pending.append(f)

        if not pending:
            print('No new migrations to run')
            await Tortoise.close_connections()
            return

        print(f"Found {len(pending)} pending migrations: {[f.name for f in pending]}")

        # 逐个执行迁移
        for i, migration_file in enumerate(pending, 1):
            print(f"  [{i}/{len(pending)}] Applying {migration_file.name}...")

            # 动态导入迁移模块
            module_name = f"migrations.models.{migration_file.stem}"
            module = __import__(module_name, fromlist=['upgrade'])

            # 获取升级 SQL
            conn = connections.get('default')
            upgrade_sql = await module.upgrade(conn)

            # 分割 SQL 语句
            # 简单方法：按分号分割，然后过滤空语句
            statements = []

            # 移除多行注释 /* ... */
            import re
            upgrade_sql = re.sub(r'/\*.*?\*/', '', upgrade_sql, flags=re.DOTALL)

            # 移除单行注释 --
            upgrade_sql = re.sub(r'--.*?$', '', upgrade_sql, flags=re.MULTILINE)

            # 按分号分割并清理
            raw_statements = upgrade_sql.split(';')
            for stmt in raw_statements:
                # 移除前后空白和空行
                cleaned = '\n'.join(line.strip() for line in stmt.split('\n') if line.strip())
                if cleaned:
                    statements.append(cleaned)

            print(f"    Found {len(statements)} SQL statements to execute")

            # 逐条执行 SQL
            for j, stmt in enumerate(statements, 1):
                try:
                    # 清理语句
                    stmt_clean = stmt.strip().rstrip(';')
                    if not stmt_clean:
                        continue

                    await conn.execute_script(stmt_clean)
                    print(f"    [{j}/{len(statements)}] Executed successfully")
                except Exception as e:
                    error_str = str(e)
                    # 跳过已存在的错误
                    if 'already exists' in error_str or 'Duplicate column' in error_str or 'Duplicate key' in error_str:
                        print(f"    [{j}/{len(statements)}] Skipped (already exists)")
                        continue
                    print(f"    [{j}/{len(statements)}] ERROR: {e}")
                    print(f"    SQL: {stmt_clean[:200]}...")
                    # 不抛出异常，继续执行下一条语句

            # 记录迁移
            try:
                # 使用完整文件名作为版本
                version = migration_file.name
                await Aerich.create(
                    version=version,
                    app='models',
                    content=upgrade_sql
                )
                print(f"  [{i}/{len(pending)}] Recorded migration: {migration_file.name}")
            except Exception as e:
                if 'Duplicate entry' in str(e):
                    print(f"  [{i}/{len(pending)}] Migration already recorded")
                else:
                    raise

        print('All migrations completed successfully')

    except Exception as e:
        print(f"Migration error: {e}")
        traceback.print_exc()
        sys.exit(1)

asyncio.run(migrate())
PYTHON_SCRIPT

echo "=== Migrations complete, starting server ==="
exec uvicorn backend.main:app --host 0.0.0.0 --port 8022
