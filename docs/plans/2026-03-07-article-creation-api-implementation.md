# 文章创建接口改造实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标：** 改造文章创建接口，支持本地上传（必填字段）和 URL 导入（同步 AI 提取）

**架构：**
- 本地上传：直接存储文件，html_path 为空，用户提供 title/summary/keywords
- URL 导入：同步 AI 提取，成功后保存，失败则返回错误

**技术栈：**
- FastAPI + TortoiseORM + Pydantic
- 火山引擎 AI API
- aiofiles（异步文件操作）

---

## Task 1: 更新 Schema 验证

**Files:**
- Modify: `backend/schemas/article.py`

**Step 1: 更新 ArticleFromHtmlUrlRequest**

确保 URL 导入请求 schema 包含 title 字段：

```python
class ArticleFromHtmlUrlRequest(BaseModel):
    """从 HTML URL 导入文章请求"""
    url: str = Field(..., min_length=1, max_length=1000)
    tag_ids: Optional[List[int]] = []
    title: Optional[str] = None  # 可选的自定义标题
```

**Step 2: 提交**

```bash
git add backend/schemas/article.py
git commit -m "refactor: 更新 URL 导入 Schema，添加可选 title 字段"
```

---

## Task 2: 添加文件定位工具函数

**Files:**
- Modify: `backend/utils/article_storage.py`

**Step 1: 添加 get_article_file_content 函数**

```python
async def get_article_file_content(article_id: int, html_path: Optional[str], original_filename: Optional[str]) -> str:
    """
    根据文章信息获取文件内容

    优先使用 html_path（URL 导入），否则使用 original_filename（本地上传）

    Args:
        article_id: 文章 ID
        html_path: HTML 文件相对路径
        original_filename: 原始文件名

    Returns:
        文件内容

    Raises:
        FileNotFoundError: 文件不存在
    """
    # URL 导入：使用 html_path
    if html_path:
        full_path = os.path.join(settings.upload_dir, html_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"文章文件不存在: {html_path}")
        async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
            return await f.read()

    # 本地上传：使用 id + original_filename
    elif original_filename:
        file_path = os.path.join(
            settings.upload_dir,
            "articles",
            str(article_id),
            original_filename
        )
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文章文件不存在: {original_filename}")
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.read()

    else:
        raise FileNotFoundError("文章文件不存在")
```

**Step 2: 提交**

```bash
git add backend/utils/article_storage.py
git commit -m "feat: 添加通用文件读取函数，支持两种来源"
```

---

## Task 3: 更新本地上传控制器函数

**Files:**
- Modify: `backend/controllers/article_controller.py`

**Step 1: 更新 create_article_from_file 函数签名和验证**

```python
async def create_article_from_file(
    file_data: Tuple[bytes, str],
    title: str,           # 改为必填
    summary: str,         # 改为必填
    keywords: str,        # 改为必填
    author_id: int,
    tag_ids: Optional[List[int]] = None
) -> ArticleResponse:
    """
    通过上传文件创建文章

    Args:
        file_data: (文件内容, 文件名) 元组
        title: 文章标题（必填）
        summary: 文章摘要（必填）
        keywords: 关键词（必填）
        author_id: 作者 ID
        tag_ids: 标签 ID 列表

    Returns:
        创建的文章响应

    Raises:
        ValueError: 参数验证失败
    """
    content_bytes, filename = file_data

    # 验证必填字段
    if not title:
        raise ValueError("标题为必填项")
    if not summary:
        raise ValueError("摘要为必填项")
    if not keywords:
        raise ValueError("关键词为必填项")

    # 创建文章记录（获取 ID）
    article = await Article.create(
        title=title,
        summary=summary,
        keywords=keywords,
        author_id=author_id,
        original_filename=filename,
        # html_path 保持为 null
        # original_html_url 保持为 null
    )

    # 创建目录并保存原始文件
    article_dir = os.path.join(settings.upload_dir, "articles", str(article.id))
    os.makedirs(article_dir, exist_ok=True)

    file_path = os.path.join(article_dir, filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content_bytes)

    # 关联标签
    if tag_ids:
        tags = await Tag.filter(id__in=tag_ids)
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
        html_path=article.html_path,  # null
        processing_status=article.processing_status,
        original_html_url=article.original_html_url  # null
    )
```

**主要变更：**
- title, summary, keywords 改为必填参数
- 移除文件转换逻辑
- html_path 保持为 null
- 直接保存原始文件

**Step 2: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "refactor: 更新本地上传函数，添加必填验证，移除转换逻辑"
```

---

## Task 4: 更新 URL 导入控制器函数

**Files:**
- Modify: `backend/controllers/article_controller.py`

**Step 1: 更新 import_article_from_html_url 函数**

```python
async def import_article_from_html_url(
    url: str,
    author_id: int,
    tag_ids: Optional[List[int]] = None,
    title: Optional[str] = None
) -> ArticleResponse:
    """
    从 URL 导入 HTML 文章（同步 AI 提取）

    Args:
        url: 网页链接
        author_id: 作者 ID
        tag_ids: 标签 ID 列表
        title: 可选的自定义标题

    Returns:
        创建的文章响应

    Raises:
        ValueError: 各种导入错误
    """
    from backend.utils.html_fetcher import fetch_html, clean_html, rewrite_base_urls
    from backend.utils.ai_extractor import extract_article_from_url
    from backend.utils.article_storage import save_html_content

    # 1. 检查 URL 是否已存在
    existing = await Article.filter(original_html_url=url).first()
    if existing:
        raise ValueError("该文章已导入")

    # 2. 下载 HTML
    try:
        raw_html = await fetch_html(url)
    except Exception as e:
        raise ValueError(f"无法访问网页: {str(e)}")

    # 3. 清洗 HTML
    cleaned_html, extracted_title = clean_html(raw_html)

    # 4. 同步调用 AI 提取
    try:
        ai_result = await extract_article_from_url(
            url=url,
            html_content=cleaned_html
        )
    except Exception as e:
        # AI 提取失败，返回错误，不保存
        raise ValueError(f"AI 提取失败: {str(e)}")

    # 5. 使用 AI 提取的结果
    final_title = title or ai_result.get("title", extracted_title)
    final_summary = ai_result.get("summary", "")
    final_keywords = ai_result.get("keywords", "")

    # 6. 创建文章记录（获取 ID）
    article = await Article.create(
        title=final_title,
        summary=final_summary,
        keywords=final_keywords,
        author_id=author_id,
        original_html_url=url,  # 保存源 URL
        processing_status="completed"
    )

    # 7. 保存 HTML 文件
    try:
        html_path = await save_html_content(article.id, cleaned_html)
        article.html_path = html_path
        await article.save()
    except Exception as e:
        # 回滚：删除文章和文件
        await article.delete()
        from backend.utils.article_storage import delete_article_files
        await delete_article_files(article.id)
        raise ValueError(f"文件保存失败: {str(e)}")

    # 8. 关联标签
    if tag_ids:
        tags = await Tag.filter(id__in=tag_ids)
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
        original_filename=article.original_filename,  # null
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags],
        html_content=cleaned_html,
        html_path=article.html_path,
        processing_status=article.processing_status,
        original_html_url=article.original_html_url  # 源 URL
    )
```

**主要变更：**
- 添加 title 参数（可选）
- 同步调用 AI 提取（不是后台任务）
- AI 失败则抛出异常，不保存
- 保存 original_html_url
- 移除 BackgroundTasks 依赖

**Step 2: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "refactor: 更新 URL 导入函数，同步 AI 提取，失败不保存"
```

---

## Task 5: 更新 API 路由

**Files:**
- Modify: `backend/api/v1/endpoints/articles/router.py`

**Step 1: 移除后台任务相关代码**

删除 `run_ai_extraction` 函数和 BackgroundTasks 依赖。

**Step 2: 更新本地上传接口**

```python
@router.post("/upload", response_model=SuccessResponse[ArticleResponse])
async def upload_file_to_create_article(
    file: UploadFile = File(...),
    title: str = Form(...),           # 改为必填
    summary: str = Form(...),         # 改为必填
    keywords: str = Form(...),        # 改为必填
    tag_ids: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    上传本地文件创建文章

    - 直接保存文件，不转换
    - title, summary, keywords 为必填项
    """
    try:
        # 验证文件大小
        content = await file.read()
        if len(content) > settings.max_file_size:
            raise HTTPException(status_code=413, detail="文件过大")

        # 解析标签
        tag_id_list = [int(t) for t in tag_ids.split(",")] if tag_ids else []

        result = await create_article_from_file(
            file_data=(content, file.filename),
            title=title,
            summary=summary,
            keywords=keywords,
            author_id=current_user.id,
            tag_ids=tag_id_list
        )
        return SuccessResponse(data=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Step 3: 更新 URL 导入接口**

```python
@router.post("/from-url-html", response_model=SuccessResponse[ArticleResponse])
async def import_html_article_from_url(
    request: ArticleFromHtmlUrlRequest,
    current_user: User = Depends(get_current_user)
):
    """
    从 URL 导入 HTML 文章

    - 同步 AI 提取，失败则不保存
    - 保存源 URL 到数据库
    """
    try:
        result = await import_article_from_html_url(
            url=request.url,
            author_id=current_user.id,
            tag_ids=request.tag_ids,
            title=request.title
        )

        # 注意：不再使用后台任务，AI 提取在 import_article_from_html_url 中同步完成
        return SuccessResponse(data=ArticleResponse(**result))

    except ValueError as e:
        if "已导入" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"无法访问网页: {e.response.status_code}")
```

**Step 4: 移除导入**

```python
# 移除
from fastapi import ... BackgroundTasks  # 删除 BackgroundTasks
```

**Step 5: 提交**

```bash
git add backend/api/v1/endpoints/articles/router.py
git commit -m "refactor: 更新文章创建路由，添加必填验证，移除后台任务"
```

---

## Task 6: 更新文件读取函数

**Files:**
- Modify: `backend/controllers/article_controller.py`

**Step 1: 更新 get_article_html_content 函数**

```python
async def get_article_html_content(article_id: int) -> str:
    """
    获取文章的 HTML 内容

    支持两种来源：
    - URL 导入：使用 html_path
    - 本地上传：使用 original_filename

    Args:
        article_id: 文章 ID

    Returns:
        HTML 内容

    Raises:
        ValueError: 文章不存在或没有文件
    """
    from backend.utils.article_storage import get_article_file_content

    article = await Article.get(id=article_id)

    if not article:
        raise ValueError("文章不存在")

    # 使用通用文件读取函数
    return await get_article_file_content(
        article_id=article_id,
        html_path=article.html_path,
        original_filename=article.original_filename
    )
```

**Step 2: 提交**

```bash
git add backend/controllers/article_controller.py
git commit -m "refactor: 更新文件读取函数，支持两种来源"
```

---

## Task 7: 更新 get_article_by_id 函数

**Files:**
- Modify: `backend/controllers/article_controller.py`

**Step 1: 更新函数以使用新的文件读取逻辑**

```python
async def get_article_by_id(article_id: int) -> ArticleResponse:
    """获取文章详情，从文件读取内容"""
    from backend.utils.article_storage import get_article_file_content

    article = await Article.get_or_none(id=article_id).prefetch_related("tags")
    if not article:
        raise ValueError("文章不存在")

    article.view_count += 1
    await article.save()

    # 从文件读取内容（支持两种来源）
    html_content = None
    try:
        html_content = await get_article_file_content(
            article_id=article_id,
            html_path=article.html_path,
            original_filename=article.original_filename
        )
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
git commit -m "refactor: 更新 get_article_by_id 使用通用文件读取函数"
```

---

## Task 8: 创建测试

**Files:**
- Create: `backend/tests/test_article_api.py`

**Step 1: 创建测试文件**

```python
# backend/tests/test_article_api.py
import pytest
from httpx import AsyncClient
from backend.models import Article

@pytest.mark.asyncio
async def test_upload_article_missing_required_fields(async_client: AsyncClient, auth_headers):
    """测试本地上传缺少必填字段"""
    # 准备测试文件
    files = {"file": ("test.html", b"<html><body>Test</body></html>", "text/html")}

    # 缺少 summary
    data = {
        "title": "Test Title",
        "keywords": "test"
    }

    response = await async_client.post("/api/v1/articles/upload", files=files, data=data, headers=auth_headers)
    assert response.status_code == 400
    assert "摘要为必填项" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_article_success(async_client: AsyncClient, auth_headers):
    """测试本地上传成功"""
    files = {"file": ("test.html", b"<html><body>Test Content</body></html>", "text/html")}
    data = {
        "title": "Test Article",
        "summary": "Test summary",
        "keywords": "test,api"
    }

    response = await async_client.post("/api/v1/articles/upload", files=files, data=data, headers=auth_headers)
    assert response.status_code == 200

    result = response.json()["data"]
    assert result["title"] == "Test Article"
    assert result["summary"] == "Test summary"
    assert result["keywords"] == "test,api"
    assert result["html_path"] is None
    assert result["original_filename"] == "test.html"

@pytest.mark.asyncio
async def test_import_from_url_ai_failure(async_client: AsyncClient, auth_headers, mocker):
    """测试 URL 导入 AI 失败"""
    # Mock AI 提取失败
    async def mock_ai_extract(*args, **kwargs):
        raise ValueError("AI service unavailable")

    mocker.patch("backend.controllers.article_controller.extract_article_from_url", mock_ai_extract)

    data = {"url": "https://example.com/article"}
    response = await async_client.post("/api/v1/articles/from-url-html", json=data, headers=auth_headers)

    assert response.status_code == 400
    assert "AI 提取失败" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_article_from_local_upload(async_client: AsyncClient, auth_headers):
    """测试获取本地上传的文章"""
    # 先创建文章
    files = {"file": ("test.html", b"<html><body>Local File</body></html>", "text/html")}
    data = {
        "title": "Local Article",
        "summary": "Local summary",
        "keywords": "local"
    }

    upload_response = await async_client.post("/api/v1/articles/upload", files=files, data=data, headers=auth_headers)
    article_id = upload_response.json()["data"]["id"]

    # 获取文章
    response = await async_client.get(f"/api/v1/articles/{article_id}", headers=auth_headers)
    assert response.status_code == 200

    result = response.json()["data"]
    assert result["html_content"] == "<html><body>Local File</body></html>"
```

**Step 2: 提交**

```bash
git add backend/tests/test_article_api.py
git commit -m "test: 添加文章创建 API 测试"
```

---

## Task 9: 端到端测试

**Step 1: 启动服务**

```bash
cd backend
python main.py
```

**Step 2: 测试本地上传**

```bash
curl -X POST http://localhost:8000/api/v1/articles/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.html" \
  -F "title=Test Article" \
  -F "summary=This is a test" \
  -F "keywords=test,api"
```

**Step 3: 测试 URL 导入**

```bash
curl -X POST http://localhost:8000/api/v1/articles/from-url-html \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article"
  }'
```

**Step 4: 验证文件存储**

```bash
ls backend/uploads/articles/
# 应该看到两种存储方式：
# - {id}/{original_filename}  (本地上传)
# - {id}/index.html           (URL 导入)
```

---

## 完成清单

- [ ] Schema 更新完成
- [ ] 文件定位工具函数添加
- [ ] 本地上传函数更新（必填验证，直接存储）
- [ ] URL 导入函数更新（同步 AI，失败不保存）
- [ ] API 路由更新
- [ ] 文件读取函数更新
- [ ] 测试创建完成
- [ ] E2E 测试通过

---

## 验证点

1. **本地上传验证**
   - title/summary/keywords 为空时返回 400
   - 文件直接保存，不转换
   - html_path 为 null
   - original_html_url 为 null

2. **URL 导入验证**
   - AI 提取失败时返回错误，不保存文章
   - AI 提取成功后保存，包含 summary 和 keywords
   - original_html_url 保存源 URL
   - html_path 指向 index.html

3. **文件读取验证**
   - 两种来源的文章都能正确读取内容
