# 文章纯文件存储实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标：** 将文章内容从数据库迁移到本地 HTML 文件存储，实现文件上传、读取、删除的完整流程。

**架构：**
- 删除 Article 模型的 `content` 字段
- 保留 `html_path` 字段存储文件相对路径
- 上传时保存为 HTML 文件到 `uploads/articles/{id}/index.html`
- 读取时从文件系统加载内容

**技术栈：**
- FastAPI + TortoiseORM + Pydantic
- aiofiles（异步文件操作）
- pytest（测试）

---

## 前置准备

### Task 0: 环境确认

**Step 1: 确认项目结构**

运行以下命令确认项目结构：

```bash
ls backend/models/
ls backend/controllers/
ls backend/schemas/
ls backend/utils/
```

预期输出应包含：`article.py`, `article_controller.py`, `article.py`

**Step 2: 检查现有依赖**

```bash
cat backend/requirements.txt | grep -E "(aiofiles|pytest)"
```

如果没有 `aiofiles`，安装它：

```bash
pip install aiofiles
```

---

## 第一部分：数据库迁移

### Task 1: 创建数据库迁移文件

**Files:**
- Create: `migrations/models/3_20260307_reset_articles.py`

**Step 1: 创建迁移文件**

```python
# migrations/models/3_20260307_reset_articles.py
from aerich.migrate import Migrate


class ResetArticles(Migrate):
    """重置文章表，移除 content 字段"""

    async def upgrade(self):
        upgrade_sql = """
        -- 删除旧表
        DROP TABLE IF EXISTS `article_tags`;
        DROP TABLE IF EXISTS `articles`;

        -- 创建新表（不含 content 字段）
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

        -- 重建关联表
        CREATE TABLE IF NOT EXISTS `article_tags` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `article_id` INT NOT NULL,
            `tag_id` INT NOT NULL,
            UNIQUE KEY `article_tag_unique` (`article_id`, `tag_id`),
            FOREIGN KEY (`article_id`) REFERENCES `articles`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE
        );
        """
        await self.execute(upgrade_sql)

    async def downgrade(self):
        downgrade_sql = """
        DROP TABLE IF EXISTS `article_tags`;
        DROP TABLE IF EXISTS `articles`;
        """
        await self.execute(downgrade_sql)
```

**Step 2: 运行迁移**

```bash
aerich upgrade
```

预期输出：迁移成功，无错误

**Step 3: 验证表结构**

```bash
mysql -u root -p knowledge-system -e "DESCRIBE articles;"
```

预期输出：应显示没有 `content` 字段

**Step 4: 提交**

```bash
git add migrations/models/3_20260307_reset_articles.py
git commit -m "feat: 创建文章表重置迁移，移除 content 字段"
```

---

### Task 2: 更新 Article 模型

**Files:**
- Modify: `backend/models/article.py`

**Step 1: 修改模型定义**

```python
# backend/models/article.py
from tortoise import fields
from tortoise.models import Model


class Article(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    # 删除: content = fields.TextField()
    original_filename = fields.CharField(max_length=255, null=True)
    source_url = fields.CharField(max_length=1000, null=True)
    summary = fields.TextField(null=True)
    keywords = fields.CharField(max_length=500, null=True)
    author = fields.ForeignKeyField("models.User", related_name="articles", on_delete=fields.CASCADE)
    view_count = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    html_path = fields.CharField(max_length=500, null=True)
    processing_status = fields.CharField(max_length=20, default="pending")
    original_html_url = fields.CharField(max_length=1000, null=True)

    tags: fields.ManyToManyRelation["Tag"] = fields.ManyToManyField(
        "models.Tag", related_name="articles", through="article_tags"
    )

    class Meta:
        table = "articles"

    def __str__(self):
        return self.title
```

**Step 2: 提交**

```bash
git add backend/models/article.py
git commit -m "refactor: 移除 Article 模型的 content 字段"
```

---

## 第二部分：Schema 更新

### Task 3: 更新 Schema 定义

**Files:**
- Modify: `backend/schemas/article.py`

**Step 1: 更新 Schema**

完整替换文件内容：

```python
# backend/schemas/article.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    # 删除: content: str
    source_url: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None

class ArticleCreate(ArticleBase):
    tag_ids: Optional[List[int]] = []

    # Import type: "direct" (直接创建), "file" (文件上传), "html" (URL 导入)
    import_type: Literal["direct", "file", "html"] = "direct"

    # 新增：用于文件上传或 HTML 导入时的内容
    html_content: Optional[str] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    # 删除: content: Optional[str] = None
    source_url: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class TagInfo(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True

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
    original_html_url: Optional[str] = None

    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    q: Optional[str] = None
    tags: Optional[List[int]] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

class ArticleFromHtmlUrlRequest(BaseModel):
    """从 HTML URL 导入文章请求"""
    url: str = Field(..., min_length=1, max_length=1000)
    tag_ids: Optional[List[int]] = []

class ArticleFromHtmlUrlResponse(BaseModel):
    """从 HTML URL 导入文章响应"""
    article_id: int
    status: str
    message: str

class ArticleHtmlResponse(ArticleResponse):
    """包含 HTML 内容的文章响应（与 ArticleResponse 合并）"""
    pass
```

**Step 2: 提交**

```bash
git add backend/schemas/article.py
git commit -m "refactor: 更新 Schema，移除 content 字段，添加 html_content"
```

---

## 第三部分：工具函数

### Task 4: 创建文件存储工具函数

**Files:**
- Create: `backend/utils/article_storage.py`

**Step 1: 创建存储工具函数**

```python
# backend/utils/article_storage.py
import os
import shutil
from typing import Optional
from pathlib import Path

import aiofiles

from backend.settings.config import settings


def get_article_dir(article_id: int) -> str:
    """获取文章存储目录路径"""
    return os.path.join(settings.upload_dir, "articles", str(article_id))


def get_html_path(article_id: int) -> str:
    """获取 HTML 文件路径"""
    return os.path.join(get_article_dir(article_id), "index.html")


def get_relative_html_path(article_id: int) -> str:
    """获取 HTML 文件相对路径（用于存储到数据库）"""
    return f"articles/{article_id}/index.html"


async def ensure_article_dir(article_id: int) -> str:
    """确保文章目录存在"""
    article_dir = get_article_dir(article_id)
    os.makedirs(article_dir, exist_ok=True)
    return article_dir


async def save_html_content(article_id: int, html_content: str) -> str:
    """
    保存 HTML 内容到文件

    Returns:
        相对路径
    """
    await ensure_article_dir(article_id)

    html_path = get_html_path(article_id)
    async with aiofiles.open(html_path, "w", encoding="utf-8") as f:
        await f.write(html_content)

    return get_relative_html_path(article_id)


async def read_html_content(article_id: int) -> str:
    """
    读取 HTML 文件内容

    Raises:
        FileNotFoundError: 文件不存在
    """
    html_path = get_html_path(article_id)

    if not os.path.exists(html_path):
        raise FileNotFoundError(f"文章内容文件不存在: {html_path}")

    async with aiofiles.open(html_path, "r", encoding="utf-8") as f:
        return await f.read()


async def delete_article_files(article_id: int) -> None:
    """删除文章相关文件"""
    article_dir = get_article_dir(article_id)

    if os.path.exists(article_dir):
        shutil.rmtree(article_dir)
```

**Step 2: 提交**

```bash
git add backend/utils/article_storage.py
git commit -m "feat: 添加文章文件存储工具函数"
```

---

## 第四部分：业务逻辑层

### Task 5: 更新 create_article 函数

**Files:**
- Modify: `backend/controllers/article_controller.py:94-183`

**Step 1: 更新 create_article 函数**

```python
# backend/controllers/article_controller.py
async def create_article(
    data: ArticleCreate,
    author_id: int,
    file_data: Optional[tuple[bytes, str]] = None
) -> ArticleResponse:
    """
    创建文章

    Args:
        data: 文章数据
        author_id: 作者ID
        file_data: (文件内容, 文件名) 元组，仅用于 import_type="file"

    Returns:
        创建的文章响应
    """
    from backend.utils.article_storage import save_html_content

    import_type = data.import_type or "direct"

    # 处理文件上传（import_type="file"）
    if import_type == "file":
        if not file_data:
            raise ValueError("文件上传需要提供文件")
        if not data.html_content:
            raise ValueError("文件上传需要提供 HTML 内容")

        content_bytes, filename = file_data

        # 创建文章记录（获取ID）
        article = await Article.create(
            title=data.title,
            source_url=data.source_url,
            summary=data.summary,
            keywords=data.keywords,
            author_id=author_id,
            original_filename=filename
        )

        try:
            # 保存 HTML 内容到文件
            html_path = await save_html_content(article.id, data.html_content)
            article.html_path = html_path
            await article.save()

            # 保存原始文件
            article_dir = os.path.join(settings.upload_dir, "articles", str(article.id))
            original_file_path = os.path.join(article_dir, filename)
            async with aiofiles.open(original_file_path, "wb") as f:
                await f.write(content_bytes)

        except Exception as e:
            # 回滚：删除文章和文件
            await article.delete()
            from backend.utils.article_storage import delete_article_files
            await delete_article_files(article.id)
            raise ValueError(f"文件保存失败: {str(e)}")

    # 处理直接创建（import_type="direct"）
    elif import_type == "direct":
        article = await Article.create(
            title=data.title,
            source_url=data.source_url,
            summary=data.summary,
            keywords=data.keywords,
            author_id=author_id
        )

        # 如果提供了 HTML 内容，保存到文件
        if data.html_content:
            try:
                html_path = await save_html_content(article.id, data.html_content)
                article.html_path = html_path
                await article.save()
            except Exception as e:
                await article.delete()
                raise ValueError(f"文件保存失败: {str(e)}")

    else:
        raise ValueError(f"不支持的导入类型: {import_type}")

    # 关联标签
    if data.tag_ids:
        tags = await Tag.filter(id__in=data.tag_ids)
        if tags:
            await article.tags.add(*tags)

    await article.fetch_related("tags")
    return ArticleResponse(
        id=article.id,
        title=article.title,
        source_url=article.source_url,
        summary=article.summary,
        keywords=article.keywords,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags],
        html_path=article.html_path,
        processing_status=article.processing_status,
        original_html_url=article.original_html_url
    )
```

**Step 2: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "refactor: 更新 create_article 使用文件存储"
```

---

### Task 6: 更新 get_article_by_id 函数

**Files:**
- Modify: `backend/controllers/article_controller.py:185-204`

**Step 1: 更新函数实现**

```python
# backend/controllers/article_controller.py
async def get_article_by_id(article_id: int) -> ArticleResponse:
    """获取文章详情，从文件读取内容"""
    from backend.utils.article_storage import read_html_content

    article = await Article.get_or_none(id=article_id).prefetch_related("tags")
    if not article:
        raise ValueError("文章不存在")

    article.view_count += 1
    await article.save()

    # 从文件读取 HTML 内容
    html_content = None
    if article.html_path:
        try:
            html_content = await read_html_content(article.id)
        except FileNotFoundError:
            # 文件不存在，返回 None
            pass

    return ArticleResponse(
        id=article.id,
        title=article.title,
        source_url=article.source_url,
        summary=article.summary,
        keywords=article.keywords,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags],
        html_content=html_content,
        html_path=article.html_path,
        processing_status=article.processing_status,
        original_html_url=article.original_html_url
    )
```

**Step 2: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "refactor: 更新 get_article_by_id 从文件读取内容"
```

---

### Task 7: 更新 update_article 函数

**Files:**
- Modify: `backend/controllers/article_controller.py:206-241`

**Step 1: 移除 content 更新逻辑**

```python
# backend/controllers/article_controller.py
async def update_article(article_id: int, data: ArticleUpdate, user_id: int, is_admin: bool = False) -> ArticleResponse:
    from backend.utils.article_storage import save_html_content, read_html_content

    article = await Article.get_or_none(id=article_id).prefetch_related("tags")
    if not article:
        raise ValueError("文章不存在")
    if article.author_id != user_id and not is_admin:
        raise ValueError("无权编辑此文章")

    if data.title:
        article.title = data.title
    # 删除: if data.content: article.content = data.content
    if data.source_url is not None:
        article.source_url = data.source_url
    if data.summary is not None:
        article.summary = data.summary
    if data.keywords is not None:
        article.keywords = data.keywords
    await article.save()

    if data.tag_ids is not None:
        await article.tags.clear()
        tags = await Tag.filter(id__in=data.tag_ids)
        await article.tags.add(*tags)
        await article.fetch_related("tags")

    # 读取 HTML 内容
    html_content = None
    if article.html_path:
        try:
            html_content = await read_html_content(article.id)
        except FileNotFoundError:
            pass

    return ArticleResponse(
        id=article.id,
        title=article.title,
        source_url=article.source_url,
        summary=article.summary,
        keywords=article.keywords,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags],
        html_content=html_content,
        html_path=article.html_path,
        processing_status=article.processing_status,
        original_html_url=article.original_html_url
    )
```

**Step 2: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "refactor: 更新 update_article 移除 content 处理"
```

---

### Task 8: 更新 delete_article 函数

**Files:**
- Modify: `backend/controllers/article_controller.py:243-250`

**Step 1: 添加文件删除逻辑**

```python
# backend/controllers/article_controller.py
async def delete_article(article_id: int, user_id: int, is_admin: bool = False) -> bool:
    from backend.utils.article_storage import delete_article_files

    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")
    if article.author_id != user_id and not is_admin:
        raise ValueError("无权删除此文章")

    # 删除文件
    await delete_article_files(article_id)

    # 删除数据库记录
    await article.delete()
    return True
```

**Step 2: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "refactor: 更新 delete_article 删除关联文件"
```

---

### Task 9: 更新 list_articles 和 search_articles

**Files:**
- Modify: `backend/controllers/article_controller.py:252-310`

**Step 1: 移除 content 字段，更新响应构建**

```python
# backend/controllers/article_controller.py
async def list_articles(page: int = 1, size: int = 20, tag_id: Optional[int] = None, author_id: Optional[int] = None) -> tuple[List[ArticleResponse], int]:
    query = Article.all()
    if tag_id:
        query = query.filter(tags__id=tag_id)
    if author_id:
        query = query.filter(author_id=author_id)
    total = await query.count()
    articles = await query.prefetch_related("tags").offset((page - 1) * size).limit(size)
    return (
        [
            ArticleResponse(
                id=a.id,
                title=a.title,
                # 删除: content=a.content
                source_url=a.source_url,
                summary=a.summary,
                keywords=a.keywords,
                author_id=a.author_id,
                original_filename=a.original_filename,
                view_count=a.view_count,
                created_at=a.created_at,
                updated_at=a.updated_at,
                tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in a.tags],
                html_path=a.html_path,
                processing_status=a.processing_status,
                original_html_url=a.original_html_url
            ) for a in articles
        ],
        total
    )


async def search_articles(query: SearchQuery) -> tuple[List[ArticleResponse], int]:
    articles_query = Article.all()
    if query.q:
        # 只搜索元数据字段，不搜索 content
        articles_query = articles_query.filter(
            Q(title__icontains=query.q) |
            Q(summary__icontains=query.q) |
            Q(keywords__icontains=query.q)
        )
    if query.tags:
        articles_query = articles_query.filter(tags__id__in=query.tags)
    total = await articles_query.count()
    articles = await articles_query.prefetch_related("tags").distinct().offset(
        (query.page - 1) * query.size
    ).limit(query.size)
    return (
        [
            ArticleResponse(
                id=a.id,
                title=a.title,
                source_url=a.source_url,
                summary=a.summary,
                keywords=a.keywords,
                author_id=a.author_id,
                original_filename=a.original_filename,
                view_count=a.view_count,
                created_at=a.created_at,
                updated_at=a.updated_at,
                tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in a.tags],
                html_path=a.html_path,
                processing_status=a.processing_status,
                original_html_url=a.original_html_url
            ) for a in articles
        ],
        total
    )
```

**Step 2: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "refactor: 更新 list_articles 和 search_articles"
```

---

### Task 10: 更新 create_article_from_file

**Files:**
- Modify: `backend/controllers/article_controller.py:14-92`

**Step 1: 更新函数实现**

```python
# backend/controllers/article_controller.py
async def create_article_from_file(
    file_data: Tuple[bytes, str],
    author_id: int,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    keywords: Optional[str] = None,
    tag_ids: Optional[List[int]] = None
) -> ArticleResponse:
    """
    通过上传文件创建文章

    Args:
        file_data: (文件内容, 文件名) 元组
        author_id: 作者ID
        title: 可选的标题（不提供则从文件名提取）
        summary: 可选的摘要
        keywords: 可选的关键词
        tag_ids: 标签ID列表

    Returns:
        创建的文章响应
    """
    from backend.utils.article_storage import save_html_content

    content_bytes, filename = file_data

    # 创建文章记录（获取ID）
    article = await Article.create(
        title=title or filename,
        summary=summary,
        keywords=keywords,
        author_id=author_id,
        original_filename=filename
    )

    # 创建存储目录 articles/{article_id}/
    article_dir = os.path.join(settings.upload_dir, "articles", str(article.id))
    os.makedirs(article_dir, exist_ok=True)

    # 保存原始文件
    original_file_path = os.path.join(article_dir, filename)
    async with aiofiles.open(original_file_path, "wb") as f:
        await f.write(content_bytes)

    # 转换为 HTML
    from backend.utils.converters import convert_document
    try:
        html_content, extracted_title = await convert_document(original_file_path, filename)
        article.title = title or extracted_title or filename

        # 保存 HTML 内容到文件
        html_path = await save_html_content(article.id, html_content)
        article.html_path = html_path
        await article.save()
    except Exception as e:
        # 转换失败，删除文章和文件
        await article.delete()
        import shutil
        from backend.utils.article_storage import delete_article_files
        await delete_article_files(article.id)
        raise ValueError(f"文件转换失败: {str(e)}")

    # 关联标签
    if tag_ids:
        tags = await Tag.filter(id__in=tag_ids)
        if tags:
            await article.tags.add(*tags)

    await article.fetch_related("tags")

    # 读取 HTML 内容用于响应
    from backend.utils.article_storage import read_html_content
    html_content_response = None
    try:
        html_content_response = await read_html_content(article.id)
    except FileNotFoundError:
        pass

    return ArticleResponse(
        id=article.id,
        title=article.title,
        source_url=article.source_url,
        summary=article.summary,
        keywords=article.keywords,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags],
        html_content=html_content_response,
        html_path=article.html_path,
        processing_status=article.processing_status,
        original_html_url=article.original_html_url
    )
```

**Step 2: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "refactor: 更新 create_article_from_file 使用文件存储"
```

---

## 第五部分：API 路由更新

### Task 11: 更新 API 路由（如果需要）

**检查是否有直接的 API 路由文件需要更新**

运行命令查找路由文件：

```bash
find backend -name "*route*.py" -o -name "*api*.py" | grep -v __pycache__
```

如果找到，检查是否需要更新请求/响应处理。

**可能的文件：** `backend/api/v1/endpoints/articles.py` 或类似路径

---

## 第六部分：测试

### Task 12: 创建单元测试

**Files:**
- Create: `tests/test_article_storage.py`

**Step 1: 创建测试文件**

```python
# tests/test_article_storage.py
import pytest
import os
import tempfile
import shutil

from backend.utils.article_storage import (
    get_article_dir,
    get_html_path,
    get_relative_html_path,
    save_html_content,
    read_html_content,
    delete_article_files
)


class TestArticleStorage:
    """文章文件存储工具测试"""

    @pytest.fixture
    def temp_dir(self, monkeypatch):
        """临时目录 fixture"""
        temp_dir = tempfile.mkdtemp()
        # 注意：需要 mock settings.upload_dir
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_get_article_dir(self):
        """测试获取文章目录路径"""
        article_id = 123
        result = get_article_dir(article_id)
        assert "articles" in result
        assert str(article_id) in result

    def test_get_html_path(self):
        """测试获取 HTML 文件路径"""
        article_id = 456
        result = get_html_path(article_id)
        assert result.endswith("index.html")
        assert "456" in result

    def test_get_relative_html_path(self):
        """测试获取相对路径"""
        article_id = 789
        result = get_relative_html_path(article_id)
        assert result == f"articles/{article_id}/index.html"

    @pytest.mark.asyncio
    async def test_save_and_read_html_content(self):
        """测试保存和读取 HTML 内容"""
        article_id = 999
        test_content = "<html><body><h1>Test Article</h1></body></html>"

        # 保存
        relative_path = await save_html_content(article_id, test_content)
        assert relative_path == f"articles/{article_id}/index.html"

        # 读取
        read_content = await read_html_content(article_id)
        assert read_content == test_content

        # 清理
        await delete_article_files(article_id)

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self):
        """测试读取不存在的文件"""
        with pytest.raises(FileNotFoundError):
            await read_html_content(999999)

    @pytest.mark.asyncio
    async def test_delete_article_files(self):
        """测试删除文章文件"""
        article_id = 888
        test_content = "<html><body>Test</body></html>"

        # 创建文件
        await save_html_content(article_id, test_content)

        # 确认文件存在
        html_path = get_html_path(article_id)
        assert os.path.exists(html_path)

        # 删除
        await delete_article_files(article_id)

        # 确认文件已删除
        assert not os.path.exists(html_path)
```

**Step 2: 运行测试**

```bash
pytest tests/test_article_storage.py -v
```

预期输出：所有测试通过

**Step 3: 提交**

```bash
git add tests/test_article_storage.py
git commit -m "test: 添加文章存储工具单元测试"
```

---

### Task 13: 创建集成测试

**Files:**
- Create: `tests/test_article_controller_integration.py`

**Step 1: 创建集成测试**

```python
# tests/test_article_controller_integration.py
import pytest
from backend.controllers.article_controller import (
    create_article,
    get_article_by_id,
    update_article,
    delete_article,
    search_articles
)
from backend.schemas.article import ArticleCreate, ArticleUpdate


@pytest.mark.asyncio
async def test_create_and_get_article(db_session, test_user):
    """测试创建和获取文章"""
    # 创建
    article_data = ArticleCreate(
        title="Test Article",
        summary="Test summary",
        keywords="test",
        import_type="direct",
        html_content="<html><body><h1>Test Content</h1></body></html>"
    )

    article = await create_article(article_data, test_user.id)
    assert article.id is not None
    assert article.title == "Test Article"
    assert article.html_path is not None

    # 获取
    fetched = await get_article_by_id(article.id)
    assert fetched.id == article.id
    assert fetched.html_content == "<html><body><h1>Test Content</h1></body></html>"

    # 清理
    await delete_article(article.id, test_user.id, is_admin=True)


@pytest.mark.asyncio
async def test_search_articles_no_content_search(db_session, test_user):
    """测试搜索不包含内容字段"""
    # 创建两篇文章
    await create_article(
        ArticleCreate(
            title="Python Tutorial",
            summary="Learn Python",
            keywords="python,programming",
            html_content="<html><body>Python content</body></html>"
        ),
        test_user.id
    )

    await create_article(
        ArticleCreate(
            title="Java Guide",
            summary="Learn Java",
            keywords="java,programming",
            html_content="<html><body>Java content</body></html>"
        ),
        test_user.id
    )

    # 搜索标题
    results, total = await search_articles(SearchQuery(q="Python"))
    assert total == 1
    assert results[0].title == "Python Tutorial"

    # 搜索摘要
    results, total = await search_articles(SearchQuery(q="Learn"))
    assert total == 2


@pytest.mark.asyncio
async def test_delete_article_removes_files(db_session, test_user):
    """测试删除文章同时删除文件"""
    article = await create_article(
        ArticleCreate(
            title="To Delete",
            html_content="<html><body>Delete me</body></html>"
        ),
        test_user.id
    )

    # 确认文件存在
    from backend.utils.article_storage import get_html_path
    import os
    html_path = get_html_path(article.id)
    assert os.path.exists(html_path)

    # 删除
    await delete_article(article.id, test_user.id, is_admin=True)

    # 确认文件已删除
    assert not os.path.exists(html_path)
```

**Step 2: 运行集成测试**

```bash
pytest tests/test_article_controller_integration.py -v
```

预期输出：所有测试通过

**Step 3: 提交**

```bash
git add tests/test_article_controller_integration.py
git commit -m "test: 添加文章控制器集成测试"
```

---

## 第七部分：验证和清理

### Task 14: 端到端验证

**Step 1: 启动后端服务**

```bash
cd backend
python main.py
```

**Step 2: 测试 API**

使用 curl 或 Postman 测试：

```bash
# 创建文章
curl -X POST http://localhost:8000/api/v1/articles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Article",
    "summary": "Test",
    "keywords": "test",
    "import_type": "direct",
    "html_content": "<html><body><h1>Hello World</h1></body></html>"
  }'

# 获取文章
curl http://localhost:8000/api/v1/articles/1 \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索文章
curl http://localhost:8000/api/v1/articles/search?q=Test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Step 3: 验证文件存储**

```bash
ls backend/uploads/articles/1/
cat backend/uploads/articles/1/index.html
```

预期输出：应看到 index.html 文件且包含正确内容

**Step 4: 检查数据库**

```bash
mysql -u root -p knowledge-system -e "SELECT id, title, html_path FROM articles LIMIT 5;"
```

预期输出：html_path 应该有值，content 字段不存在

---

### Task 15: 最终检查

**Step 1: 运行所有测试**

```bash
pytest tests/ -v --cov=backend
```

预期输出：所有测试通过，覆盖率 > 80%

**Step 2: 检查类型错误**

```bash
mypy backend/
```

预期输出：无类型错误

**Step 3: 最终提交**

```bash
git add .
git commit -m "feat: 完成文章纯文件存储实现"
```

---

## 完成清单

- [ ] 数据库迁移完成
- [ ] Article 模型更新
- [ ] Schema 更新
- [ ] 文件存储工具创建
- [ ] 所有 controller 函数更新
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] E2E 测试通过
- [ ] 代码覆盖率 > 80%
- [ ] 文档更新

---

## 后续步骤

1. **前端适配：** 更新前端代码处理新的响应结构（`html_content` 替代 `content`）
2. **性能监控：** 监控文件读取性能，考虑添加缓存
3. **备份策略：** 实现定期备份 `uploads/` 目录
