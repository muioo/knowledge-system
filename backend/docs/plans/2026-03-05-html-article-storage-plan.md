# HTML 文章存储与 AI 提取功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-step.

**Goal:** 从 URL 导入网络文章，下载 HTML 原文和图片到本地，异步使用 AI 提取摘要和关键词

**Architecture:**
- HTML 下载器使用 readability 清洗内容
- 图片处理器并发下载并重写链接
- FastAPI BackgroundTasks 处理异步 AI 提取
- 文件存储在 `/uploads/articles/{id}/` 目录结构

**Tech Stack:**
- FastAPI, TortoiseORM
- readability-lxml, httpx, beautifulsoup4
- volcenginesdkarkruntime (火山引擎 AI)

---

## Task 1: 添加数据库字段

**Files:**
- Modify: `backend/models/article.py`

**Step 1: 阅读当前模型**

读取 `backend/models/article.py` 了解现有结构

**Step 2: 添加新字段**

```python
# 在 Article 类中添加以下字段：
html_path = fields.CharField(max_length=500, null=True)
processing_status = fields.CharField(max_length=20, default="pending")  # pending/processing/completed/failed
original_html_url = fields.CharField(max_length=1000, null=True)
```

**Step 3: 生成迁移文件**

```bash
cd E:/PyCharm/Code/FastAPI/knowledge-system
aerich migrate --name add_html_article_fields
```

预期输出：生成新的迁移文件

**Step 4: 应用迁移**

```bash
aerich upgrade
```

预期输出：`Upgrade success`

**Step 5: 验证迁移**

```bash
python -c "from backend.models import Article; print('Article model loaded successfully')"
```

预期输出：无错误

**Step 6: 提交**

```bash
git add backend/models/article.py migrations/
git commit -m "feat: add html storage fields to Article model"
```

---

## Task 2: 创建 HTML 下载器

**Files:**
- Create: `backend/utils/html_fetcher.py`

**Step 1: 创建文件并编写基础结构**

```python
"""HTML 下载和清洗工具"""
import httpx
from readability-lxml import Document
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Tuple


async def fetch_html(url: str) -> str:
    """
    获取网页原始 HTML

    Args:
        url: 网页链接

    Returns:
        原始 HTML 内容

    Raises:
        httpx.HTTPStatusError: 网页无法访问
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


def clean_html(html: str) -> Tuple[str, str]:
    """
    使用 readability 清洗 HTML

    Args:
        html: 原始 HTML

    Returns:
        (清洗后的 HTML, 标题)
    """
    doc = Document(html)
    title = doc.title()
    cleaned_html = doc.summary()

    return cleaned_html, title


async def rewrite_base_urls(html: str, base_url: str) -> str:
    """
    将相对路径转换为绝对路径

    Args:
        html: HTML 内容
        base_url: 基础 URL

    Returns:
        重写后的 HTML
    """
    soup = BeautifulSoup(html, 'html.parser')

    # 处理 img 标签
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and not src.startswith(('http://', 'https://', 'data:')):
            abs_url = urljoin(base_url, src)
            img['src'] = abs_url

    return str(soup)
```

**Step 2: 安装依赖**

```bash
pip install readability-lxml
```

预期输出：安装成功

**Step 3: 更新 requirements.txt**

在 `backend/requirements.txt` 添加：
```
readability-lxml==0.8.1
```

**Step 4: 测试导入**

```bash
python -c "from backend.utils.html_fetcher import fetch_html; print('Import successful')"
```

预期输出：`Import successful`

**Step 5: 提交**

```bash
git add backend/utils/html_fetcher.py backend/requirements.txt
git commit -m "feat: add HTML fetcher with readability support"
```

---

## Task 3: 创建图片处理器

**Files:**
- Create: `backend/utils/image_processor.py`

**Step 1: 创建文件**

```python
"""图片下载和链接重写工具"""
import httpx
import os
import asyncio
from urllib.parse import urlparse
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple


async def extract_images(html: str) -> List[str]:
    """
    提取 HTML 中所有图片 URL

    Args:
        html: HTML 内容

    Returns:
        图片 URL 列表（去重）
    """
    soup = BeautifulSoup(html, 'html.parser')
    urls = set()

    for img in soup.find_all('img'):
        src = img.get('src')
        if src and src.startswith(('http://', 'https://')):
            urls.add(src)

    return list(urls)


async def download_image(url: str, save_path: str) -> bool:
    """
    下载单张图片

    Args:
        url: 图片 URL
        save_path: 保存路径

    Returns:
        是否下载成功
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as f:
                f.write(response.content)

        return True
    except Exception:
        return False


async def download_images_batch(urls: List[str], base_dir: str) -> Dict[str, str]:
    """
    批量下载图片

    Args:
        urls: 图片 URL 列表
        base_dir: 基础目录

    Returns:
        {原始 URL: 本地路径/原始 URL} 映射
    """
    mapping = {}
    semaphore = asyncio.Semaphore(10)  # 限制并发数

    async def download_with_semaphore(url: str, index: int):
        async with semaphore:
            # 生成本地文件名
            ext = os.path.splitext(urlparse(url).path)[1] or '.jpg'
            filename = f"img_{index:04d}{ext}"
            save_path = os.path.join(base_dir, 'images', filename)

            success = await download_image(url, save_path)
            if success:
                mapping[url] = f"images/{filename}"
            else:
                mapping[url] = url  # 失败保留原 URL

    tasks = [download_with_semaphore(url, i) for i, url in enumerate(urls)]
    await asyncio.gather(*tasks)

    return mapping


async def rewrite_image_links(html: str, url_mapping: Dict[str, str]) -> str:
    """
    重写 HTML 中的图片链接

    Args:
        html: HTML 内容
        url_mapping: URL 映射字典

    Returns:
        重写后的 HTML
    """
    soup = BeautifulSoup(html, 'html.parser')

    for img in soup.find_all('img'):
        src = img.get('src')
        if src in url_mapping:
            new_src = url_mapping[src]
            img['src'] = new_src

            # 标记失败的图片
            if new_src == src and new_src.startswith('http'):
                img['data-download-failed'] = 'true'

    return str(soup)
```

**Step 2: 测试导入**

```bash
python -c "from backend.utils.image_processor import extract_images; print('Import successful')"
```

预期输出：`Import successful`

**Step 3: 提交**

```bash
git add backend/utils/image_processor.py
git commit -m "feat: add image processor for downloading and rewriting links"
```

---

## Task 4: 扩展 AI 提取器支持异步

**Files:**
- Modify: `backend/utils/ai_extractor.py`

**Step 1: 添加异步提取函数**

在文件末尾添加：

```python
async def extract_article_async(article_id: int) -> bool:
    """
    异步提取文章摘要和关键词（用于后台任务）

    Args:
        article_id: 文章 ID

    Returns:
        是否提取成功
    """
    from backend.models import Article
    import aiofiles

    # 重试逻辑
    for attempt in range(3):
        try:
            # 获取文章
            article = await Article.get(id=article_id)

            # 更新状态为处理中
            article.processing_status = "processing"
            await article.save()

            # 读取本地 HTML 文件
            if not article.html_path:
                return False

            html_path = article.html_path
            if not os.path.isabs(html_path):
                html_path = os.path.join("backend", html_path)

            async with aiofiles.open(html_path, 'r', encoding='utf-8') as f:
                html_content = await f.read()

            # 调用 AI 提取
            result = await extract_article_from_url(
                article.original_html_url or "",
                html_content
            )

            # 更新文章
            article.summary = result.get("summary")
            article.keywords = result.get("keywords")
            article.processing_status = "completed"
            await article.save()

            return True

        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(5)
                continue
            else:
                # 最后一次尝试失败
                try:
                    article = await Article.get(id=article_id)
                    article.processing_status = "failed"
                    await article.save()
                except:
                    pass
                return False

    return False
```

**Step 2: 添加必要的导入**

在文件顶部添加：
```python
import asyncio
import os
```

**Step 3: 测试导入**

```bash
python -c "from backend.utils.ai_extractor import extract_article_async; print('Import successful')"
```

预期输出：`Import successful`

**Step 4: 提交**

```bash
git add backend/utils/ai_extractor.py
git commit -m "feat: add async article extraction with retry logic"
```

---

## Task 5: 创建 Schema

**Files:**
- Modify: `backend/schemas/article.py`

**Step 1: 添加新的 Schema 类**

在文件末尾添加：

```python
class ArticleFromHtmlUrlRequest(BaseModel):
    """从 HTML URL 导入文章请求"""
    url: str = Field(..., min_length=1, max_length=1000)
    tag_ids: Optional[List[int]] = []


class ArticleFromHtmlUrlResponse(BaseModel):
    """从 HTML URL 导入文章响应"""
    article_id: int
    status: str  # pending
    message: str


class ArticleHtmlResponse(ArticleResponse):
    """包含 HTML 内容的文章响应"""
    html_content: Optional[str] = None
    html_path: Optional[str] = None
    processing_status: Optional[str] = None
```

**Step 2: 测试导入**

```bash
python -c "from backend.schemas.article import ArticleFromHtmlUrlRequest; print('Import successful')"
```

预期输出：`Import successful`

**Step 3: 提交**

```bash
git add backend/schemas/article.py
git commit -m "feat: add schemas for HTML article import"
```

---

## Task 6: 创建控制器函数

**Files:**
- Modify: `backend/controllers/article_controller.py`

**Step 1: 添加导入**

在文件顶部添加：
```python
from backend.utils.html_fetcher import fetch_html, clean_html, rewrite_base_urls
from backend.utils.image_processor import extract_images, download_images_batch, rewrite_image_links
from backend.utils.ai_extractor import extract_article_async
import os
import aiofiles
from pathlib import Path
from backend.settings.config import settings
```

**Step 2: 添加导入 HTML 文章函数**

在文件末尾添加：

```python
async def import_article_from_html_url(url: str, author_id: int, tag_ids: list = None) -> dict:
    """
    从 URL 导入 HTML 文章

    Args:
        url: 网页链接
        author_id: 作者 ID
        tag_ids: 标签 ID 列表

    Returns:
        {article_id, status, message}

    Raises:
        ValueError: 各种导入错误
    """
    from backend.models import Article

    # 检查 URL 是否已存在
    existing = await Article.filter(original_html_url=url).first()
    if existing:
        raise ValueError("该文章已导入")

    # 1. 下载 HTML
    raw_html = await fetch_html(url)

    # 2. 清洗 HTML
    cleaned_html, title = clean_html(raw_html)

    # 3. 重写相对路径为绝对路径
    full_html = rewrite_base_urls(cleaned_html, url)

    # 4. 创建文章记录（获取 ID）
    article = await Article.create(
        title=title,
        content="",  # 稍后由 AI 填充
        author_id=author_id,
        original_html_url=url,
        processing_status="pending"
    )

    try:
        # 5. 创建存储目录
        article_dir = os.path.join("uploads", "articles", str(article.id))
        images_dir = os.path.join(article_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        # 6. 提取并下载图片
        image_urls = await extract_images(full_html)
        url_mapping = {}

        if image_urls:
            url_mapping = await download_images_batch(image_urls, article_dir)

        # 7. 重写图片链接
        final_html = rewrite_image_links(full_html, url_mapping)

        # 8. 保存 HTML 文件
        html_path = os.path.join(article_dir, "index.html")
        async with aiofiles.open(html_path, 'w', encoding='utf-8') as f:
            await f.write(final_html)

        # 9. 更新文章记录
        article.html_path = f"uploads/articles/{article.id}/index.html"
        await article.save()

        # 10. 关联标签
        if tag_ids:
            await article.tags.add(*tag_ids)

        return {
            "article_id": article.id,
            "status": "pending",
            "message": "文章导入成功，AI 提取中"
        }

    except Exception as e:
        # 回滚：删除文章记录和文件
        await article.delete()
        import shutil
        if os.path.exists(article_dir):
            shutil.rmtree(article_dir)
        raise ValueError(f"保存失败: {str(e)}")


async def get_article_html_content(article_id: int) -> str:
    """
    获取文章的 HTML 内容

    Args:
        article_id: 文章 ID

    Returns:
        HTML 内容

    Raises:
        ValueError: 文章不存在或没有 HTML 内容
    """
    from backend.models import Article

    article = await Article.get(id=article_id)

    if not article.html_path:
        raise ValueError("该文章没有 HTML 内容")

    html_path = article.html_path
    if not os.path.isabs(html_path):
        html_path = os.path.join("backend", html_path)

    async with aiofiles.open(html_path, 'r', encoding='utf-8') as f:
        return await f.read()
```

**Step 3: 测试导入**

```bash
python -c "from backend.controllers.article_controller import import_article_from_html_url; print('Import successful')"
```

预期输出：`Import successful`

**Step 4: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "feat: add controller for HTML article import"
```

---

## Task 7: 创建 API 端点

**Files:**
- Modify: `backend/api/v1/endpoints/articles/router.py`

**Step 1: 添加导入**

在文件顶部的导入部分添加：
```python
from fastapi import BackgroundTasks
from backend.schemas.article import ArticleFromHtmlUrlRequest, ArticleFromHtmlUrlResponse, ArticleHtmlResponse
from backend.controllers.article_controller import import_article_from_html_url, get_article_html_content
```

**Step 2: 添加后台任务函数**

在 `upload_document` 函数后添加：

```python
async def run_ai_extraction(article_id: int):
    """后台任务：执行 AI 提取"""
    from backend.utils.ai_extractor import extract_article_async
    await extract_article_async(article_id)
```

**Step 3: 添加导入 HTML 文章端点**

在 `create_article_from_url` 函数后添加：

```python
@router.post("/from-url-html", response_model=SuccessResponse[ArticleFromHtmlUrlResponse])
async def import_html_article_from_url(
    request: ArticleFromHtmlUrlRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    从 URL 导入 HTML 文章

    - 下载并清洗 HTML
    - 下载图片到本地
    - 异步提取摘要和关键词
    """
    try:
        result = await import_article_from_html_url(
            url=request.url,
            author_id=current_user.id,
            tag_ids=request.tag_ids
        )

        # 添加后台 AI 提取任务
        background_tasks.add_task(run_ai_extraction, result["article_id"])

        return SuccessResponse(data=ArticleFromHtmlUrlResponse(**result))

    except ValueError as e:
        if "已导入" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"无法访问网页: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/{article_id}/html", response_model=SuccessResponse[ArticleHtmlResponse])
async def get_article_html(
    article_id: int,
    current_user: User = Depends(get_current_user)
):
    """获取文章的 HTML 内容"""
    try:
        # 获取基本信息
        result = await get_article_by_id(article_id)

        # 获取 HTML 内容
        html_content = await get_article_html_content(article_id)

        # 组合响应
        response_data = ArticleHtmlResponse(
            **result.model_dump(),
            html_content=html_content
        )

        return SuccessResponse(data=response_data)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Step 4: 测试导入**

```bash
python -c "from backend.main import app; print('Import successful')"
```

预期输出：`Import successful`

**Step 5: 提交**

```bash
git add backend/api/v1/endpoints/articles/router.py
git commit -m "feat: add API endpoints for HTML article import and viewing"
```

---

## Task 8: 更新 Article 查询端点

**Files:**
- Modify: `backend/api/v1/endpoints/articles/router.py`

**Step 1: 修改 get_article 端点**

找到 `get_article` 函数，修改响应类型：

```python
@router.get("/{article_id}", response_model=SuccessResponse[ArticleHtmlResponse])
async def get_article(
    article_id: int,
    current_user: User = Depends(get_current_user)
):
    """获取文章详情（包含 HTML 内容）"""
    try:
        # 获取基本信息
        result = await get_article_by_id(article_id)

        # 如果有 HTML 路径，读取 HTML 内容
        html_content = None
        if hasattr(result, 'html_path') and result.html_path:
            try:
                html_content = await get_article_html_content(article_id)
            except:
                pass  # HTML 读取失败不影响基本信息返回

        # 组合响应
        response_data = ArticleHtmlResponse(
            **result.model_dump(),
            html_content=html_content
        )

        return SuccessResponse(data=response_data)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Step 2: 提交**

```bash
git add backend/api/v1/endpoints/articles/router.py
git commit -m "feat: update article detail endpoint to include HTML content"
```

---

## Task 9: 添加测试

**Files:**
- Create: `backend/tests/test_html_article.py`

**Step 1: 创建测试文件**

```python
"""HTML 文章导入功能测试"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_import_html_article_success(client: AsyncClient, auth_headers):
    """测试成功导入 HTML 文章"""
    # 使用测试 URL
    response = await client.post(
        "/api/v1/articles/from-url-html",
        json={"url": "https://example.com/article"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["article_id"] > 0
    assert data["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_import_html_article_duplicate_url(client: AsyncClient, auth_headers):
    """测试重复 URL 导入"""
    url = "https://example.com/test-unique"

    # 第一次导入
    response1 = await client.post(
        "/api/v1/articles/from-url-html",
        json={"url": url},
        headers=auth_headers
    )
    assert response1.status_code == 200

    # 第二次导入相同 URL
    response2 = await client.post(
        "/api/v1/articles/from-url-html",
        json={"url": url},
        headers=auth_headers
    )
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_import_html_article_invalid_url(client: AsyncClient, auth_headers):
    """测试无效 URL"""
    response = await client.post(
        "/api/v1/articles/from-url-html",
        json={"url": "https://this-domain-does-not-exist-12345.com"},
        headers=auth_headers
    )

    assert response.status_code == 400
```

**Step 2: 运行测试**

```bash
cd backend
pytest tests/test_html_article.py -v
```

预期输出：测试执行（可能失败因为需要真实网络）

**Step 3: 提交**

```bash
git add backend/tests/test_html_article.py
git commit -m "test: add tests for HTML article import"
```

---

## Task 10: 更新文档

**Files:**
- Create: `backend/docs/html-article-import.md`

**Step 1: 创建文档**

```markdown
# HTML 文章导入功能

## 功能说明

支持从网络 URL 导入文章，自动下载 HTML 原文和图片到本地存储。

## API 接口

### 导入 HTML 文章

```
POST /api/v1/articles/from-url-html
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://example.com/article",
  "tag_ids": [1, 2]
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "article_id": 123,
    "status": "pending",
    "message": "文章导入成功，AI 提取中"
  }
}
```

### 获取文章 HTML 内容

```
GET /api/v1/articles/{id}/html
Authorization: Bearer <token>
```

## 错误码

- 400: URL 无法访问或格式错误
- 409: URL 已导入
- 500: 服务器内部错误

## 文件存储

```
/uploads/articles/
  └── {article_id}/
      ├── index.html
      └── images/
          ├── img_0001.jpg
          └── img_0002.png
```
```

**Step 2: 提交**

```bash
git add backend/docs/html-article-import.md
git commit -m "docs: add HTML article import documentation"
```

---

## Task 11: 最终验证

**Step 1: 完整导入测试**

```bash
cd E:/PyCharm/Code/FastAPI/knowledge-system
python -c "from backend.main import app; print('Application loads successfully')"
```

预期输出：`Application loads successfully`

**Step 2: 检查依赖**

```bash
cd backend
pip list | grep -E "readability|httpx|beautifulsoup"
```

预期输出：列出所有相关依赖

**Step 3: 查看迁移状态**

```bash
aerich history
```

预期输出：包含新的迁移记录

**Step 4: 最终提交**

```bash
git add -A
git commit -m "feat: complete HTML article storage and AI extraction feature"
```

---

## 执行总结

实现完成后，您将拥有：

1. ✅ URL 去重检测
2. ✅ HTML 下载与 readability 清洗
3. ✅ 并发图片下载与链接重写
4. ✅ 本地文件存储
5. ✅ 异步 AI 提取摘要和关键词
6. ✅ 完整的错误处理
7. ✅ RESTful API 接口
8. ✅ 测试覆盖

**关键文件：**
- `backend/utils/html_fetcher.py` - HTML 下载器
- `backend/utils/image_processor.py` - 图片处理器
- `backend/utils/ai_extractor.py` - AI 提取器（扩展）
- `backend/api/v1/endpoints/articles/router.py` - API 端点
- `backend/models/article.py` - 数据模型（新字段）
