#!/bin/sh
set -e

echo "=== Waiting for MySQL to be ready ==="
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
    except Exception:
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

echo "=== Running aerich migrations ==="
# 逐条执行迁移，解决 MySQL 5.7 多语句执行问题
python -c "
import asyncio
from aerich import Command
from backend.settings.config import settings

async def migrate():
    config = {
        'connections': {'default': settings.database_url},
        'apps': {
            'models': {
                'models': ['backend.models.user', 'backend.models.article', 'backend.models.tag', 'backend.models.reading'],
                'default_connection': 'default',
            }
        }
    }
    command = Command(tortoise_config=config)
    await command.init()
    migrated = await command.upgrade(run_in_transaction=True)
    if migrated:
        print(f'Successfully migrated: {migrated}')
    else:
        print('No new migrations to run')

asyncio.run(migrate())
"

echo "=== Migrations complete, starting server ==="
exec uvicorn backend.main:app --host 0.0.0.0 --port 8022
