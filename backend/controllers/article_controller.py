import os
from typing import List, Optional, Tuple

from tortoise.queryset import Q

import aiofiles
from backend.models import Article, Tag
from backend.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, SearchQuery, TagInfo
from backend.utils.html_fetcher import fetch_html, clean_html, rewrite_base_urls
from backend.utils.image_processor import extract_images, download_images_batch, rewrite_image_links
from backend.utils.ai_extractor import extract_article_from_url
from backend.settings.config import settings


async def create_article_from_file(
    file_data: Tuple[bytes, str],
    title: str,
    summary: str,
    keywords: str,
    author_id: int,
    tag_ids: Optional[List[int]] = None
) -> ArticleResponse:
    """
    通过上传文件创建文章

    Args:
        file_data: (文件内容, 文件名) 元组
        title: 文章标题（必填）
        summary: 文章摘要（必填）
        keywords: 文章关键词（必填）
        author_id: 作者ID
        tag_ids: 标签ID列表

    Returns:
        创建的文章响应

    Raises:
        ValueError: 必填字段为空时抛出异常
    """
    import logging

    # 验证必填字段
    if not title:
        raise ValueError("标题为必填项")
    if not summary:
        raise ValueError("摘要为必填项")
    if not keywords:
        raise ValueError("关键词为必填项")

    content_bytes, filename = file_data

    # 预先验证标签ID
    if tag_ids:
        valid_tags = await Tag.filter(id__in=tag_ids)
        valid_tag_ids = {t.id for t in valid_tags}
        invalid_tag_ids = set(tag_ids) - valid_tag_ids
        if invalid_tag_ids:
            raise ValueError(f"无效的标签ID: {list(invalid_tag_ids)}")

    # 创建文章记录（获取ID）
    article = await Article.create(
        title=title,
        summary=summary,
        keywords=keywords,
        author_id=author_id,
        original_filename=filename
    )

    logging.info(f"Created article with ID: {article.id}")

    try:
        # 创建目录并保存原始文件
        article_dir = os.path.join(settings.upload_dir, "articles", str(article.id))
        os.makedirs(article_dir, exist_ok=True)

        file_path = os.path.join(article_dir, filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content_bytes)

        # 关联标签 - 确保文章存在后再关联
        if tag_ids:
            logging.info(f"Associating tags {tag_ids} with article {article.id}")

            # 刷新文章对象
            await article.refresh_from_db()

            # 逐个关联标签
            for tag_id in tag_ids:
                try:
                    await article.tags.add(tag_id)
                    logging.info(f"Associated tag {tag_id} with article {article.id}")
                except Exception as tag_error:
                    logging.error(f"Failed to associate tag {tag_id}: {tag_error}")

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

    except Exception as e:
        # 出错时删除文章记录和文件
        logging.error(f"Error during article creation: {str(e)}", exc_info=True)
        try:
            await article.delete()
        except:
            pass
        import shutil
        if os.path.exists(article_dir):
            shutil.rmtree(article_dir)
        raise ValueError(f"保存失败: {str(e)}")
        # 创建文章记录（获取ID）
        article = await Article.create(
            title=title,
            summary=summary,
            keywords=keywords,
            author_id=author_id,
            original_filename=filename
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
            html_path=article.html_path,
            processing_status=article.processing_status,
            original_html_url=article.original_html_url
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
    """获取文章详情，从文件读取内容"""
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")

    # 预加载标签关系
    await article.fetch_related("tags")

    article.view_count += 1
    await article.save()

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

async def update_article(article_id: int, data: ArticleUpdate, user_id: int, is_admin: bool = False) -> ArticleResponse:
    
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")
    if article.author_id != user_id and not is_admin:
        raise ValueError("无权编辑此文章")
    if data.title:
        article.title = data.title
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

async def list_articles(page: int = 1, size: int = 20, tag_id: Optional[int] = None, author_id: Optional[int] = None, user_id: Optional[int] = None) -> tuple[List[ArticleResponse], int]:
    """
    获取文章列表

    Args:
        user_id: 可选的用户ID，用于填充阅读状态信息
    """
    query = Article.all()
    if tag_id:
        query = query.filter(tags__id=tag_id)
    if author_id:
        query = query.filter(author_id=author_id)
    total = await query.count()
    articles = await query.prefetch_related("tags").offset((page - 1) * size).limit(size)

    # 如果提供了 user_id，获取阅读状态信息
    reading_stats_map = {}
    if user_id:
        from backend.models import ReadingStats
        article_ids = [a.id for a in articles]
        if article_ids:
            stats = await ReadingStats.filter(user_id=user_id, article_id__in=article_ids)
            for stat in stats:
                reading_stats_map[stat.article_id] = {
                    'is_read': stat.max_reading_progress >= 100 or stat.completed_reads > 0,
                    'reading_progress': stat.last_reading_progress
                }

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
                original_html_url=a.original_html_url,
                # 填充阅读状态信息
                is_read=reading_stats_map.get(a.id, {}).get('is_read'),
                reading_progress=reading_stats_map.get(a.id, {}).get('reading_progress')
            ) for a in articles
        ],
        total
    )

async def search_articles(query: SearchQuery, user_id: Optional[int] = None) -> tuple[List[ArticleResponse], int]:
    """
    搜索文章

    Args:
        query: 搜索查询对象
        user_id: 可选的用户ID，用于填充阅读状态信息
    """
    articles_query = Article.all()
    if query.q:
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

    # 如果提供了 user_id，获取阅读状态信息
    reading_stats_map = {}
    if user_id:
        from backend.models import ReadingStats
        article_ids = [a.id for a in articles]
        if article_ids:
            stats = await ReadingStats.filter(user_id=user_id, article_id__in=article_ids)
            for stat in stats:
                reading_stats_map[stat.article_id] = {
                    'is_read': stat.max_reading_progress >= 100 or stat.completed_reads > 0,
                    'reading_progress': stat.last_reading_progress
                }

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
                original_html_url=a.original_html_url,
                # 填充阅读状态信息
                is_read=reading_stats_map.get(a.id, {}).get('is_read'),
                reading_progress=reading_stats_map.get(a.id, {}).get('reading_progress')
            ) for a in articles
        ],
        total
    )


async def import_article_from_html_url(
    url: str,
    author_id: int,
    tag_ids: Optional[List[int]] = None,
    title: Optional[str] = None,
    use_ai: bool = True,
    summary: Optional[str] = None,
    keywords: Optional[str] = None,
    api_key: Optional[str] = None
) -> ArticleResponse:
    """
    从 URL 导入 HTML 文章

    Args:
        url: 网页链接
        author_id: 作者 ID
        tag_ids: 标签 ID 列表
        title: 可选标题（不提供则由 AI 提取或从HTML提取）
        use_ai: 是否使用AI提取关键词和摘要，默认为True
        summary: 手动输入的摘要（use_ai=False时使用）
        keywords: 手动输入的关键词（use_ai=False时使用）

    Returns:
        创建的文章响应

    Raises:
        ValueError: 各种导入错误
    """
    import logging

    # 预先验证标签ID
    if tag_ids:
        valid_tags = await Tag.filter(id__in=tag_ids)
        valid_tag_ids = {t.id for t in valid_tags}
        invalid_tag_ids = set(tag_ids) - valid_tag_ids
        if invalid_tag_ids:
            raise ValueError(f"无效的标签ID: {list(invalid_tag_ids)}")

    # 检查 URL 是否已存在
    existing = await Article.filter(original_html_url=url).first()
    if existing:
        raise ValueError("该文章已导入")

    # 1. 下载 HTML
    raw_html = await fetch_html(url)

    # 2. 清洗 HTML
    cleaned_html, extracted_title = clean_html(raw_html)

    # 3. 重写相对路径为绝对路径
    full_html = await rewrite_base_urls(cleaned_html, url)

    # 4. 根据参数决定是否使用AI提取
    ai_summary = None
    ai_keywords = None
    ai_title = None

    if use_ai:
        try:
            ai_result = await extract_article_from_url(
                url=url,
                html_content=cleaned_html,
                api_key=api_key
            )
            ai_summary = ai_result.get("summary")
            ai_keywords = ai_result.get("keywords")
            ai_title = ai_result.get("title")
        except Exception as e:
            logging.warning(f"AI 提取失败 (url={url}): {str(e)}")

    # 5. 确定最终的标题、摘要和关键词
    final_title = title or ai_title or extracted_title
    final_summary = summary or ai_summary or "暂无摘要"
    final_keywords = keywords or ai_keywords or ""

    # 6. 创建文章记录（获取 ID）
    article = await Article.create(
        title=final_title,
        summary=final_summary,
        keywords=final_keywords,
        author_id=author_id,
        original_html_url=url,
        processing_status="completed"
    )

    logging.info(f"Created article with ID: {article.id}")

    article_dir = None

    try:
        # 7. 创建存储目录
        article_dir = os.path.join(settings.upload_dir, "articles", str(article.id))
        images_dir = os.path.join(article_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        # 8. 提取并下载图片（传入base_url处理相对路径）
        image_urls = extract_images(full_html, base_url=url)
        url_mapping = {}

        if image_urls:
            url_mapping = await download_images_batch(image_urls, article_dir)

        # 9. 重写图片链接
        final_html = rewrite_image_links(full_html, url_mapping)

        # 10. 保存 HTML 文件
        html_path = os.path.join(article_dir, "index.html")
        async with aiofiles.open(html_path, 'w', encoding='utf-8') as f:
            await f.write(final_html)

        # 11. 更新文章记录（保存相对路径，不包含 upload_dir 部分）
        article.html_path = f"articles/{article.id}/index.html"
        await article.save()

        # 12. 关联标签 - 确保文章确实存在后再关联
        if tag_ids:
            logging.info(f"Associating tags {tag_ids} with article {article.id}")

            # 刷新文章对象，确保它是最新的
            await article.refresh_from_db()

            # 使用逐个关联的方式，更安全
            for tag_id in tag_ids:
                try:
                    await article.tags.add(tag_id)
                    logging.info(f"Associated tag {tag_id} with article {article.id}")
                except Exception as tag_error:
                    logging.error(f"Failed to associate tag {tag_id}: {tag_error}")
                    # 即使标签关联失败，也继续处理其他标签

            logging.info(f"Completed tag association for article {article.id}")

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

    except Exception as e:
        # 出错时删除文章记录和文件
        logging.error(f"Error during article import: {str(e)}", exc_info=True)
        try:
            await article.delete()
        except:
            pass
        import shutil
        if article_dir and os.path.exists(article_dir):
            shutil.rmtree(article_dir)
        raise ValueError(f"保存失败: {str(e)}")


async def get_article_html_content(article_id: int) -> str:
    """
    获取文章的 HTML 内容
    支持两种来源：
    - URL 导入：使用 html_path
    - 本地上传：使用 original_filename

    Args:
        article_id: 文章 ID

    Returns:
        处理后的 HTML 内容（图片路径已替换为 API URL）

    Raises:
        ValueError: 文章不存在或没有文件
    """
    from backend.utils.article_storage import get_article_file_content
    from bs4 import BeautifulSoup

    article = await Article.get(id=article_id)

    if not article:
        raise ValueError("文章不存在")

    # 使用通用文件读取函数
    html_content = await get_article_file_content(
        article_id=article_id,
        html_path=article.html_path,
        original_filename=article.original_filename
    )

    # 替换相对路径的图片链接为 API URL
    soup = BeautifulSoup(html_content, 'html.parser')

    for img in soup.find_all('img'):
        src = img.get('src')
        if src and not src.startswith('http') and not src.startswith('//'):
            # 相对路径，替换为 API URL
            # 移除开头的 ./ 或 /
            clean_src = src.lstrip('./').lstrip('/')
            img['src'] = f"/api/v1/media/articles/{article_id}/{clean_src}"

    # 清理可能有问题的 SVG 元素
    # 策略：移除所有 SVG，因为它们可能导致渲染问题
    for svg in soup.find_all('svg'):
        svg.decompose()

    return str(soup)
