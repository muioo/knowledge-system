from backend.models import Tag, Article
from backend.schemas.tag import TagCreate, TagUpdate, TagResponse
from backend.schemas.article import ArticleResponse, TagInfo
from typing import List, Optional

async def create_tag(data: TagCreate) -> TagResponse:
    existing = await Tag.get_or_none(name=data.name)
    if existing:
        raise ValueError("标签已存在")
    tag = await Tag.create(name=data.name, color=data.color)
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at
    )

async def get_tag_by_id(tag_id: int) -> TagResponse:
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at
    )

async def list_tags() -> List[TagResponse]:
    tags = await Tag.all()
    return [
        TagResponse(
            id=t.id,
            name=t.name,
            color=t.color,
            created_at=t.created_at
        ) for t in tags
    ]

async def update_tag(tag_id: int, data: TagUpdate) -> TagResponse:
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")
    if data.name:
        tag.name = data.name
    if data.color:
        tag.color = data.color
    await tag.save()
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at
    )

async def delete_tag(tag_id: int) -> bool:
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")
    await tag.delete()
    return True

async def get_articles_by_tag(tag_id: int, page: int = 1, size: int = 20) -> tuple[List[ArticleResponse], int]:
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")
    total = await tag.articles.all().count()
    articles = await tag.articles.all().prefetch_related("tags").offset((page - 1) * size).limit(size)
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
