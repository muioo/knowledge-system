from backend.models import Article, Tag
from backend.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, SearchQuery, TagInfo
from typing import List, Optional
from tortoise.queryset import Q

async def create_article(data: ArticleCreate, author_id: int) -> ArticleResponse:
    article = await Article.create(
        title=data.title,
        content=data.content,
        author_id=author_id
    )
    if data.tag_ids:
        tags = await Tag.filter(id__in=data.tag_ids)
        await article.tags.add(*tags)
    await article.fetch_related("tags")
    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags]
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
