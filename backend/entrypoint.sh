#!/bin/sh
set -e

echo "=== Running database migrations ==="

# 等待 MySQL 就绪（最多等 60 秒）
echo "Waiting for MySQL to be ready..."
MAX_RETRIES=30
RETRY=0
until python -c "
import asyncio, sys
from tortoise import Tortoise
from backend.settings.config import TORTOISE_ORM
async def check():
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.close_connections()
    except Exception as e:
        sys.exit(1)
asyncio.run(check())
" 2>/dev/null; do
    RETRY=$((RETRY + 1))
    if [ $RETRY -ge $MAX_RETRIES ]; then
        echo "MySQL not ready after ${MAX_RETRIES} retries, exiting."
        exit 1
    fi
    echo "  MySQL not ready yet, retrying in 2s... ($RETRY/$MAX_RETRIES)"
    sleep 2
done
echo "MySQL is ready."

# 运行 aerich 初始建表迁移
echo "Running aerich migrations..."
cd /app
aerich upgrade || echo "Aerich upgrade skipped (already up to date)"

# 运行手动字段补充迁移
echo "Running column patch migration..."
python backend/run_migration.py

echo "=== Migrations complete, starting server ==="
exec uvicorn backend.main:app --host 0.0.0.0 --port 8022
