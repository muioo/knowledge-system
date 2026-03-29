# Docker 部署数据库迁移方案

## 概述

本项目使用 **Tortoise-ORM + Aerich** 进行数据库迁移，在 Docker 容器中启动时自动执行数据库初始化和迁移。

## 关键文件

| 文件 | 作用 |
|------|------|
| `backend/entrypoint.sh` | 容器启动入口，负责等待 MySQL 就绪并执行迁移 |
| `backend/Dockerfile` | 包含换行符修复（CRLF → LF） |
| `docker-compose.yml` | 服务编排配置 |
| `init-db.sh` | 服务器端数据库初始化脚本（创建数据库和用户） |
| `migrations/models/*.py` | Aerich 迁移文件 |

## 架构说明

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker 容器启动流程                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. entrypoint.sh 开始执行                                   │
│     │                                                       │
│     ▼                                                       │
│  2. 等待 MySQL 连接成功（最多重试 30 次）                     │
│     │                                                       │
│     ▼                                                       │
│  3. 执行数据库迁移                                           │
│     ├─ 读取 migrations/models/ 目录                         │
│     ├─ 查询 aerich 表获取已应用的迁移                        │
│     ├─ 执行待执行的迁移                                      │
│     └─ 按 ;; 分割 SQL，逐条执行（兼容 MySQL 5.7）            │
│     │                                                       │
│     ▼                                                       │
│  4. 启动 FastAPI 服务 (uvicorn)                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## entrypoint.sh 核心逻辑

```bash
#!/bin/sh
# 不使用 set -e，显示错误信息便于调试

# 1. 等待 MySQL 就绪
echo "=== Waiting for MySQL to be ready ==="
python -c "检查连接..."

# 2. 执行迁移（核心代码）
echo "=== Running aerich migrations ==="
python << 'PYTHON_SCRIPT'
import asyncio
from aerich import Command
from aerich.models import Aerich
from backend.settings.config import TORTOISE_ORM
from tortoise import Tortoise, connections

async def migrate():
    await Tortoise.init(config=TORTOISE_ORM)

    # 读取迁移文件
    migrations_path = Path('migrations/models')
    migration_files = sorted(migrations_path.glob('*.py'))

    # 检查已应用的迁移
    applied = await Aerich.all().values('version')
    applied_versions = [a['version'] for a in applied]

    # 执行待执行的迁移
    for migration_file in pending:
        # 动态导入迁移模块
        module = __import__(f"migrations.models.{migration_file.stem}")
        upgrade_sql = await module.upgrade(conn)

        # 按 ;; 分割 SQL，逐条执行（兼容 MySQL 5.7）
        statements = [s.strip() for s in upgrade_sql.split(';;') if s.strip()]
        for stmt in statements:
            await conn.execute_script(stmt.rstrip(';'))

        # 记录迁移
        await Aerich.create(version=version, app='models', content=upgrade_sql)

asyncio.run(migrate())
PYTHON_SCRIPT

# 3. 启动服务
exec uvicorn backend.main:app --host 0.0.0.0 --port 8022
```

## MySQL 5.7 兼容性处理

### 问题

Aerich 生成的迁移文件使用 `;;` 作为语句分隔符，MySQL 5.7 的 `execute_script()` 无法一次性执行多语句。

### 解决方案

在 `entrypoint.sh` 中将 SQL 按 `;;` 分割，逐条执行：

```python
# 分割 SQL 语句
statements = [s.strip() for s in upgrade_sql.split(';;') if s.strip()]

# 逐条执行
for stmt in statements:
    await conn.execute_script(stmt.rstrip(';'))
```

### 迁移文件格式

```python
# migrations/models/1_20260329153659_add_reading_fields.py
async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `reading_goals` (...);;
        ALTER TABLE `reading_history` ADD `is_completed` BOOL...;;
        ALTER TABLE `reading_history` ADD `total_content_length` INT...;;
    """
```

## Dockerfile 关键配置

```dockerfile
# 复制 backend 代码
COPY backend ./backend

# 修复 entrypoint.sh 换行符（CRLF → LF）并设置可执行权限
RUN sed -i 's/\r$//' ./backend/entrypoint.sh && \
    chmod +x ./backend/entrypoint.sh

# 设置入口点
ENTRYPOINT ["./backend/entrypoint.sh"]
```

**重要**: `sed -i 's/\r$//'` 修复 Windows 换行符，避免 "exec: no such file or directory" 错误。

## docker-compose.yml 配置

### 连接外部 MySQL（宿主机）

```yaml
services:
  backend:
    environment:
      DB_HOST: host.docker.internal  # 关键：使用 host.docker.internal
      DB_PORT: 3307
      DB_USER: knowledge_user
      DB_PASSWORD: Knowledge@123
      DB_NAME: knowledge_system
    extra_hosts:
      - "host.docker.internal:host-gateway"  # Linux 需要显式映射
```

### 连接内部 MySQL（Docker 网络）

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}

  backend:
    environment:
      DB_HOST: db  # 使用服务名
    depends_on:
      db:
        condition: service_healthy
```

## 部署流程

### 1. 服务器端初始化数据库（首次部署）

```bash
# 运行 init-db.sh 创建数据库和用户
chmod +x init-db.sh
./init-db.sh
```

**init-db.sh 内容:**

```bash
#!/bin/bash
docker exec -i mysql mysql -uroot -p<密码> <<EOF
CREATE DATABASE IF NOT EXISTS knowledge_system CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'knowledge_user'@'%' IDENTIFIED BY 'Knowledge@123';
GRANT ALL PRIVILEGES ON knowledge_system.* TO 'knowledge_user'@'%';
FLUSH PRIVILEGES;
EOF
```

### 2. 构建并启动容器

```bash
# 拉取最新代码
git pull origin production

# 构建并启动
docker compose down
docker compose build --no-cache backend
docker compose up -d

# 查看日志
docker logs -f knowledge-backend
```

### 3. 验证迁移成功

```bash
# 查看后端日志
docker logs knowledge-backend

# 应该看到：
# === Waiting for MySQL to be ready ===
# MySQL is ready.
# === Running aerich migrations ===
# Found 2 pending migrations
#   [1/2] Applying 1_20260329153659_add_reading_fields.py...
#   [1/2] Applied 1_20260329153659_add_reading_fields.py
# All migrations completed successfully
# === Migrations complete, starting server ===
```

## 新项目迁移模板

### 1. 修改 Tortoise 配置

```python
# backend/settings/config.py
@property
def tortoise_orm(self) -> dict:
    return {
        "connections": {"default": self.database_url},
        "apps": {
            "models": {
                "models": ["backend.models.user", "backend.models.article"],
                "default_connection": "default",
            },
            "aerich": {
                "models": ["aerich.models"],  # 必须包含
                "default_connection": "default",
            }
        },
    }

TORTOISE_ORM = settings.tortoise_orm
```

### 2. 复制 entrypoint.sh

将本项目的 `backend/entrypoint.sh` 复制到新项目，确保：

1. MySQL 等待逻辑中的 `TORTOISE_ORM` 导入路径正确
2. 迁移文件路径 `migrations/models` 正确
3. 应用名称 `models` 与 tortoise 配置一致

### 3. 修改 Dockerfile

```dockerfile
# 修复换行符
RUN sed -i 's/\r$//' ./backend/entrypoint.sh && \
    chmod +x ./backend/entrypoint.sh

ENTRYPOINT ["./backend/entrypoint.sh"]
```

### 4. 创建 init-db.sh

```bash
#!/bin/bash
docker exec -i <mysql容器名> mysql -uroot -p<密码> <<EOF
CREATE DATABASE IF NOT EXISTS <数据库名> CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS '<用户名>'@'%' IDENTIFIED BY '<密码>';
GRANT ALL PRIVILEGES ON <数据库名>.* TO '<用户名>'@'%';
FLUSH PRIVILEGES;
EOF
```

## 故障排查

### 问题 1: "exec: no such file or directory"

**原因**: Windows 换行符 (CRLF) 导致 Linux 无法识别脚本

**解决**: 在 Dockerfile 中添加 `sed -i 's/\r$//'`

### 问题 2: MySQL 连接失败

**原因**: `DB_HOST=localhost` 在容器内指向容器本身

**解决**: 使用 `host.docker.internal`（外部 MySQL）或服务名（内部 MySQL）

### 问题 3: "You have an error in your SQL syntax"

**原因**: MySQL 5.7 无法执行多语句 SQL

**解决**: entrypoint.sh 中按 `;;` 分割 SQL 逐条执行

### 问题 4: "Migrate() takes no arguments"

**原因**: Aerich 版本 API 变化

**解决**: 手动读取迁移文件，不使用 `Migrate()` 类

## 检查清单

部署前确认：

- [ ] `backend/settings/config.py` 中 `tortoise_orm` 包含 `aerich` app
- [ ] `backend/Dockerfile` 包含 `sed -i 's/\r$//'` 换行符修复
- [ ] `docker-compose.yml` 中 `DB_HOST` 配置正确
  - 外部 MySQL: `host.docker.internal` + `extra_hosts`
  - 内部 MySQL: 服务名
- [ ] `init-db.sh` 数据库初始化脚本已执行
- [ ] `.env` 文件数据库配置正确

## 参考命令

```bash
# 查看 MySQL 容器日志
docker logs <mysql容器名>

# 进入 backend 容器调试
docker exec -it knowledge-backend bash

# 手动运行迁移测试
docker exec -it knowledge-backend python -c "
import asyncio
from backend.settings.config import TORTOISE_ORM
from tortoise import Tortoise
async def test():
    await Tortoise.init(config=TORTOISE_ORM)
    print('Database connection OK!')
    await Tortoise.close_connections()
asyncio.run(test())
"

# 查看数据库表
docker exec -i mysql mysql -uknowledge_user -p<密码> knowledge_system -e "SHOW TABLES;"

# 查看 aerich 迁移记录
docker exec -i mysql mysql -uknowledge_user -p<密码> knowledge_system -e "SELECT * FROM aerich;"
```
