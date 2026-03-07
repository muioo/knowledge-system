# 文章纯文件存储架构设计

**日期：** 2026-03-07
**作者：** Claude
**状态：** 已批准

## 概述

将文章内容从数据库 LONGTEXT 迁移到本地 HTML 文件存储，数据库只保留元数据和文件路径引用。

## 背景

当前文章系统将内容存储在数据库的 `content` 字段中。为了：
- 减少数据库存储压力
- 支持更大的文章内容
- 便于内容版本管理和备份

决定将内容改为纯文件存储。

## 需求

1. **存储格式：** HTML (.html)
2. **现有数据：** 清空重新开始
3. **搜索方式：** 仅搜索摘要/元数据
4. **内容读取：** API 直接返回文件内容

## 数据库变更

### Article 模型

**删除字段：**
- `content` (LONGTEXT)

**保留字段：**
- `html_path` - 存储相对路径 `articles/{article_id}/index.html`
- `summary` - 用于搜索
- `keywords` - 用于搜索

### 迁移 SQL

```sql
-- 删除原有表
DROP TABLE IF EXISTS `articles`;

-- 重建表（不含 content 字段）
CREATE TABLE `articles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `original_filename` VARCHAR(255) NULL,
    `source_url` VARCHAR(1000) NULL,
    `summary` TEXT NULL,
    `keywords` VARCHAR(500) NULL,
    `author_id` INT NOT NULL,
    `view_count` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `html_path` VARCHAR(500) NULL,
    `processing_status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `original_html_url` VARCHAR(1000) NULL,
    FOREIGN KEY (`author_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
);
```

## 文件存储结构

```
backend/uploads/
└── articles/
    └── {article_id}/
        ├── original.{ext}      # 原始上传文件
        └── index.html          # 转换后的 HTML 内容
```

**html_path 格式：** `articles/{article_id}/index.html`

## API 变更

### 1. 创建文章 (POST /articles)

```python
async def create_article(...):
    # 1. 创建文章记录（获取 ID）
    article = await Article.create(
        title=title,
        summary=summary,
        keywords=keywords,
        author_id=author_id,
        html_path=None  # 稍后更新
    )

    # 2. 创建目录并保存 HTML 文件
    article_dir = os.path.join(settings.upload_dir, "articles", str(article.id))
    os.makedirs(article_dir, exist_ok=True)

    html_path = os.path.join(article_dir, "index.html")
    async with aiofiles.open(html_path, "w", encoding="utf-8") as f:
        await f.write(html_content)

    # 3. 更新路径
    article.html_path = f"articles/{article.id}/index.html"
    await article.save()

    return article
```

### 2. 获取文章 (GET /articles/{id})

```python
async def get_article_by_id(article_id: int):
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")

    # 从文件读取内容
    if not article.html_path:
        raise ValueError("文章内容文件不存在")

    full_path = os.path.join(settings.upload_dir, article.html_path)
    async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
        html_content = await f.read()

    article.view_count += 1
    await article.save()

    return ArticleResponse(
        id=article.id,
        title=article.title,
        html_content=html_content,
        summary=article.summary,
        keywords=article.keywords,
        ...
    )
```

### 3. 搜索文章

```python
async def search_articles(query: str):
    # 只搜索元数据字段，不搜索内容
    return await Article.filter(
        Q(title__icontains=query) |
        Q(summary__icontains=query) |
        Q(keywords__icontains=query)
    )
```

### 4. 删除文章

```python
async def delete_article(article_id: int):
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")

    # 删除文件
    if article.html_path:
        article_dir = os.path.dirname(article.html_path)
        full_dir = os.path.join(settings.upload_dir, article_dir)
        if os.path.exists(full_dir):
            shutil.rmtree(full_dir)

    # 删除数据库记录
    await article.delete()
```

## Schema 更新

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    source_url: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None

class ArticleCreate(ArticleBase):
    tag_ids: Optional[List[int]] = []
    import_type: Literal["direct", "file", "html"] = "direct"

class ArticleResponse(ArticleBase):
    id: int
    author_id: int
    original_filename: Optional[str] = None
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInfo] = []

    # 新增字段
    html_content: Optional[str] = None
    html_path: Optional[str] = None
    processing_status: Optional[str] = None

    class Config:
        from_attributes = True
```

## 错误处理

| 场景 | HTTP 状态 | 处理方式 |
|------|-----------|---------|
| 文章不存在 | 404 | 返回"文章不存在" |
| HTML 文件不存在 | 404 | 返回"文章内容文件丢失" |
| 文件读取失败 | 500 | 记录日志，返回"读取失败" |
| 磁盘空间不足 | 500 | 创建时捕获，回滚数据库，删除部分文件 |
| 权限不足 | 403 | 检查文件/目录权限 |

## 实现文件清单

1. **数据库层**
   - `backend/models/article.py` - 修改模型，删除 content 字段
   - `migrations/models/3_20260307_reset_articles.py` - 新建迁移文件

2. **业务逻辑层**
   - `backend/controllers/article_controller.py` - 修改创建/获取/删除逻辑

3. **Schema 层**
   - `backend/schemas/article.py` - 修改响应结构

4. **工具函数** (可选新增)
   - `backend/utils/article_storage.py` - 文件存储辅助函数

## 测试计划

1. **单元测试**
   - 文件创建/读取/删除
   - 路径生成逻辑
   - 错误处理

2. **集成测试**
   - 完整的上传流程
   - 获取文章内容
   - 搜索功能
   - 删除文章

3. **边界测试**
   - 大文件上传
   - 特殊字符文件名
   - 并发创建

## 后续优化建议

1. **性能优化**
   - 添加内容缓存（Redis）
   - 实现文件压缩存储
   - 分片加载大文件

2. **功能增强**
   - AI 自动提取摘要
   - 文件版本管理
   - 增量更新机制

3. **运维支持**
   - 存储空间监控
   - 文件一致性检查
   - 备份恢复策略
