import os
from typing import List, Optional, Tuple

from tortoise.queryset import Q

import aiofiles
from backend.models import Article, Tag
from backend.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, SearchQuery, TagInfo
from backend.utils.html_fetcher import fetch_html, clean_html, rewrite_base_urls
from backend.utils.image_processor import extract_images, download_images_batch, rewrite_image_links
from backend.settings.config import settings


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
    content_bytes, filename = file_data

    # 创建文章记录（获取ID）
    article = await Article.create(
        title=title or filename,
        content="",  # 稍后由转换器填充
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

    # 转换为 markdown
    from backend.utils.converters import convert_document
    try:
        markdown_content, extracted_title = await convert_document(original_file_path, filename)
        article.title = title or extracted_title or filename
        article.content = markdown_content
        await article.save()
    except Exception as e:
        # 转换失败，删除文章和文件
        await article.delete()
        import shutil
        if os.path.exists(article_dir):
            shutil.rmtree(article_dir)
        raise ValueError(f"文件转换失败: {str(e)}")

    # 关联标签
    if tag_ids:
        tags = await Tag.filter(id__in=tag_ids)
        if tags:
            await article.tags.add(*tags)

    await article.fetch_related("tags")
    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        source_url=article.source_url,
        summary=article.summary,
        keywords=article.keywords,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags]
    )

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
                # 回滚：删除文章和文件
                await article.delete()
                from backend.utils.article_storage import delete_article_files
                await delete_article_files(article.id)
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

async def get_article_by_id(article_id: int) -> ArticleResponse:
    article = await Article.get_or_none(id=article_id).prefetch_related("tags")
    if not article:
        raise ValueError("文章不存在")
    article.view_count += 1
    await article.save()
    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        source_url=article.source_url,
        summary=article.summary,
        keywords=article.keywords,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags]
    )

async def update_article(article_id: int, data: ArticleUpdate, user_id: int, is_admin: bool = False) -> ArticleResponse:
    article = await Article.get_or_none(id=article_id).prefetch_related("tags")
    if not article:
        raise ValueError("文章不存在")
    if article.author_id != user_id and not is_admin:
        raise ValueError("无权编辑此文章")
    if data.title:
        article.title = data.title
    if data.content:
        article.content = data.content
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
    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        source_url=article.source_url,
        summary=article.summary,
        keywords=article.keywords,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags]
    )

async def delete_article(article_id: int, user_id: int, is_admin: bool = False) -> bool:
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")
    if article.author_id != user_id and not is_admin:
        raise ValueError("无权删除此文章")
    await article.delete()
    return True

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
                content=a.content,
                source_url=a.source_url,
                summary=a.summary,
                keywords=a.keywords,
                author_id=a.author_id,
                original_filename=a.original_filename,
                view_count=a.view_count,
                created_at=a.created_at,
                updated_at=a.updated_at,
                tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in a.tags]
            ) for a in articles
        ],
        total
    )

async def search_articles(query: SearchQuery) -> tuple[List[ArticleResponse], int]:
    articles_query = Article.all()
    if query.q:
        articles_query = articles_query.filter(
            Q(title__icontains=query.q) | Q(content__icontains=query.q)
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
                content=a.content,
                source_url=a.source_url,
                summary=a.summary,
                keywords=a.keywords,
                author_id=a.author_id,
                original_filename=a.original_filename,
                view_count=a.view_count,
                created_at=a.created_at,
                updated_at=a.updated_at,
                tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in a.tags]
            ) for a in articles
        ],
        total
    )


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
    # 检查 URL 是否已存在
    existing = await Article.filter(original_html_url=url).first()
    if existing:
        raise ValueError("该文章已导入")

    # 1. 下载 HTML
    raw_html = await fetch_html(url)

    # 2. 清洗 HTML
    cleaned_html, title = clean_html(raw_html)

    # 3. 重写相对路径为绝对路径
    full_html = await rewrite_base_urls(cleaned_html, url)

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
        article_dir = os.path.join(settings.upload_dir, "articles", str(article.id))
        images_dir = os.path.join(article_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        # 6. 提取并下载图片
        image_urls = extract_images(full_html)
        url_mapping = {}

        if image_urls:
            url_mapping = await download_images_batch(image_urls, article_dir)

        # 7. 重写图片链接
        final_html = rewrite_image_links(full_html, url_mapping)

        # 8. 保存 HTML 文件
        html_path = os.path.join(article_dir, "index.html")
        async with aiofiles.open(html_path, 'w', encoding='utf-8') as f:
            await f.write(final_html)

        # 9. 更新文章记录（保存相对路径，不包含 upload_dir 部分）
        article.html_path = f"articles/{article.id}/index.html"
        await article.save()

        # 10. 关联标签
        if tag_ids:
            tags = await Tag.filter(id__in=tag_ids)
            if tags:
                await article.tags.add(*tags)

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
    article = await Article.get(id=article_id)

    if not article.html_path:
        raise ValueError("该文章没有 HTML 内容")

    # 使用 settings.upload_dir 作为基础目录
    html_path = os.path.join(settings.upload_dir, article.html_path)

    async with aiofiles.open(html_path, 'r', encoding='utf-8') as f:
        return await f.read()
