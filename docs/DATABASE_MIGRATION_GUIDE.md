# 数据库迁移使用指南

本项目使用 [Aerich](https://github.com/tortoise/aerich) 作为 TortoiseORM 的数据库迁移工具。

## 配置文件

- **配置文件**: `pyproject.toml`
- **TORTOISE_ORM 配置**: `backend/settings/config.py`
- **迁移文件位置**: `migrations/`

## 常用命令

### 1. 初始化项目（仅首次使用）

```bash
# 初始化 Aerich 配置
aerich init -t backend.settings.config.TORTOISE_ORM

# 初始化数据库（创建所有表）
aerich init-db
```

### 2. 创建迁移文件

当你修改了模型（Models）后，需要创建迁移文件：

```bash
# 生成新的迁移文件
aerich migrate

# 为迁移指定描述（推荐）
aerich migrate --name "添加文章图片字段"
```

### 3. 执行迁移

将迁移应用到数据库：

```bash
# 升级到最新版本
aerich upgrade

# 升级到指定版本
aerich upgrade --to 20260308174314

# 查看迁移历史
aerich history
```

### 4. 回滚迁移

```bash
# 回滚到上一个版本
aerich downgrade

# 回滚到指定版本
aerich downgrade --to 20260308173301
```

## 工作流程

1. **修改模型**: 在 `backend/models/` 中修改模型定义
2. **生成迁移**: 运行 `aerich migrate` 生成迁移文件
3. **检查迁移**: 查看 `migrations/models/` 中的新迁移文件，确认 SQL 正确
4. **执行迁移**: 运行 `aerich upgrade` 应用到数据库

## 模型文件位置

- 用户模型: `backend/models/user.py`
- 文章模型: `backend/models/article.py`
- 标签模型: `backend/models/tag.py`
- 阅读记录模型: `backend/models/reading.py`

## 常见问题

### 错误: Unknown column 'content' in 'field list'

这表示 `aerich` 表的版本不匹配。解决方法：

```bash
# 1. 删除所有数据库表
mysql -u root -p123456 -e "USE knowledge-system; DROP TABLE IF EXISTS reading_stats; DROP TABLE IF EXISTS reading_history; DROP TABLE IF EXISTS article_tags; DROP TABLE IF EXISTS articles; DROP TABLE IF EXISTS tags; DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS aerich;"

# 2. 删除迁移文件
rm -rf migrations

# 3. 重新初始化
aerich init -t backend.settings.config.TORTOISE_ORM
aerich init-db
```

### 错误: App 'models' is already initialized

删除 `migrations` 目录后重试：

```bash
rm -rf migrations
aerich init -t backend.settings.config.TORTOISE_ORM
```

### No changes detected

模型没有变化，无需创建新迁移。

## 数据库连接信息

- **主机**: localhost
- **端口**: 3306
- **用户**: root
- **密码**: 12345
- **数据库**: knowledge-system

配置文件: `backend/.env`
