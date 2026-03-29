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
from pathlib import Path

try:
    from aerich import Command
    from aerich.models import Aerich
    from backend.settings.config import TORTOISE_ORM
    from tortoise import Tortoise, connections

    async def migrate():
        try:
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
                return

            # 获取所有迁移文件
            migration_files = sorted(migrations_path.glob('*.py'))
            if not migration_files:
                print('No migration files found')
                return

            # 获取已应用的迁移
            applied_versions = []
            try:
                applied = await Aerich.all().values('version')
                applied_versions = [a['version'] for a in applied]
            except:
                pass  # 首次运行，aerich 表还不存在

            # 找出待执行的迁移
            pending = []
            for f in migration_files:
                if f.name.startswith('0_'):
                    # 初始迁移特殊处理
                    if not applied_versions:
                        pending.append(f)
                else:
                    version = f.name.split('_')[1]
                    if version not in applied_versions:
                        pending.append(f)

            if not pending:
                print('No new migrations to run')
                await Tortoise.close_connections()
                return

            print(f"Found {len(pending)} pending migrations")

            # 逐个执行迁移
            for i, migration_file in enumerate(pending, 1):
                print(f"  [{i}/{len(pending)}] Applying {migration_file.name}...")

                # 动态导入迁移模块
                module_name = f"migrations.models.{migration_file.stem}"
                module = __import__(module_name, fromlist=['upgrade'])

                # 获取升级 SQL
                conn = connections.get('default')
                upgrade_sql = await module.upgrade(conn)

                # 分割 SQL 语句（按 ;; 分割）
                statements = [s.strip() for s in upgrade_sql.split(';;') if s.strip()]

                # 逐条执行 SQL
                for j, stmt in enumerate(statements, 1):
                    try:
                        stmt_clean = stmt.rstrip(';')
                        await conn.execute_script(stmt_clean)
                    except Exception as e:
                        error_str = str(e)
                        # 跳过已存在的错误
                        if 'already exists' in error_str or 'Duplicate column' in error_str or 'Duplicate key' in error_str:
                            print(f"    [{j}/{len(statements)}] Skipped (already exists)")
                            continue
                        print(f"    [{j}/{len(statements)}] ERROR: {e}")
                        print(f"    SQL: {stmt_clean[:100]}...")
                        raise

                # 记录迁移
                version = migration_file.stem.split('_', 1)[1]
                await Aerich.create(
                    version=version,
                    app='models',
                    content=upgrade_sql
                )
                print(f"  [{i}/{len(pending)}] Applied {migration_file.name}")

            print('All migrations completed successfully')

        except Exception as e:
            print(f"Migration error: {e}")
            traceback.print_exc()
            sys.exit(1)
        finally:
            await Tortoise.close_connections()

    asyncio.run(migrate())
except Exception as e:
    print(f"Import error: {e}")
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

echo "=== Migrations complete, starting server ==="
exec uvicorn backend.main:app --host 0.0.0.0 --port 8022
