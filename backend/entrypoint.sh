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
# 分割 SQL 语句逐条执行，解决 MySQL 5.7 多语句问题
python << 'PYTHON_SCRIPT'
import asyncio
import sys
import traceback

try:
    from aerich import Command
    from aerich.migrate import Migrate
    from backend.settings.config import TORTOISE_ORM
    from tortoise import connections

    async def migrate():
        try:
            print("Initializing aerich...")
            # 初始化 aerich
            command = Command(tortoise_config=TORTOISE_ORM, location='migrations')
            await command.init()

            print("Getting pending migrations...")
            # 获取待执行的迁移
            migrate_instance = Migrate(TORTOISE_ORM, 'migrations', app='models')
            await migrate_instance.init()

            # 检查是否有新迁移
            last_version = await migrate_instance.get_last_version()
            if not last_version:
                print('No new migrations to run')
                return

            print(f"Found migration: {last_version.version}")
            # 获取迁移 SQL
            conn = connections.get('models')
            upgrade_sql = await last_version.upgrade(conn)

            # 分割 SQL 语句（按 ;; 分割，去除空语句）
            statements = [s.strip() for s in upgrade_sql.split(';;') if s.strip()]

            print(f'Executing {len(statements)} SQL statements...')
            for i, stmt in enumerate(statements, 1):
                try:
                    # 移除结尾的分号
                    stmt = stmt.rstrip(';')
                    await conn.execute_script(stmt)
                    print(f'  [{i}/{len(statements)}] OK')
                except Exception as e:
                    print(f'  [{i}/{len(statements)}] FAILED: {e}')
                    # 如果是 CREATE TABLE 或 ALTER TABLE 已经存在，跳过
                    if 'already exists' in str(e) or 'Duplicate column' in str(e) or 'Duplicate key' in str(e):
                        print(f'  (Skipping, already exists)')
                        continue
                    raise

            # 标记迁移为已完成
            await last_version.set_applied()
            print(f'Successfully migrated: {last_version.version}')

        except Exception as e:
            print(f"Migration error: {e}")
            traceback.print_exc()
            sys.exit(1)

    asyncio.run(migrate())
except Exception as e:
    print(f"Import error: {e}")
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

echo "=== Migrations complete, starting server ==="
exec uvicorn backend.main:app --host 0.0.0.0 --port 8022
