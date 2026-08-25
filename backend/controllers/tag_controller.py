from typing import List, Optional, Set

from backend.models import Article, Tag
from backend.schemas.article import ArticleResponse, TagInfo
from backend.schemas.tag import TagCreate, TagResponse, TagUpdate
from backend.utils.tag_hierarchy import collect_descendant_tag_ids


async def _serialize_tag(tag: Tag) -> TagResponse:
    """将标签模型转换为包含直接文章数量的响应模型。"""
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        parent_id=tag.parent_id,
        created_at=tag.created_at,
        article_count=await tag.articles.all().count(),
    )


async def _validate_parent_id(tag_id: Optional[int], parent_id: Optional[int]) -> None:
    """验证父标签存在且不会把标签移动到自身或其后代下。"""
    if parent_id is None:
        return
    if tag_id == parent_id:
        raise ValueError("标签不能设置自身为父标签")

    parent = await Tag.get_or_none(id=parent_id)
    if not parent:
        raise ValueError("父标签不存在")
    if tag_id is None:
        return

    tag_pairs = await Tag.all().values_list("id", "parent_id")
    descendant_ids: Set[int] = collect_descendant_tag_ids(tag_id, tag_pairs)
    if parent_id in descendant_ids:
        raise ValueError("不能将标签移动到其子标签下")


async def create_tag(data: TagCreate) -> TagResponse:
    """创建顶级标签或指定父标签下的子标签。"""
    existing = await Tag.get_or_none(name=data.name)
    if existing:
        raise ValueError("标签已存在")
    await _validate_parent_id(None, data.parent_id)
    return await _serialize_tag(
        await Tag.create(name=data.name, color=data.color, parent_id=data.parent_id)
    )


async def get_tag_by_id(tag_id: int) -> TagResponse:
    """按 ID 获取标签及其直接文章数量。"""
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")
    return await _serialize_tag(tag)


async def list_tags() -> List[TagResponse]:
    """返回平铺标签集合，供前端按 parent_id 组装标签树。"""
    return [await _serialize_tag(tag) for tag in await Tag.all().order_by("parent_id", "id")]


async def update_tag(tag_id: int, data: TagUpdate) -> TagResponse:
    """更新标签内容或父级，并防止形成循环层级。"""
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")
    if data.name is not None:
        tag.name = data.name
    if data.color is not None:
        tag.color = data.color
    if "parent_id" in data.model_fields_set:
        await _validate_parent_id(tag_id, data.parent_id)
        tag.parent_id = data.parent_id
    await tag.save()
    return await _serialize_tag(tag)


async def delete_tag(tag_id: int) -> bool:
    """删除无子标签的标签，阻止隐式删除整个子树。"""
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")
    if await Tag.filter(parent_id=tag_id).exists():
        raise ValueError("请先删除或移动该标签的子标签")
    await tag.delete()
    return True


async def get_articles_by_tag(
    tag_id: int, page: int = 1, size: int = 20
) -> tuple[List[ArticleResponse], int]:
    """返回标签及全部后代标签关联的分页文章。"""
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")
    tag_ids = collect_descendant_tag_ids(
        tag_id,
        await Tag.all().values_list("id", "parent_id"),
    )
    query = Article.filter(tags__id__in=tag_ids).distinct()
    total = await query.count()
    articles = await query.prefetch_related("tags").offset((page - 1) * size).limit(size)
    return [
        ArticleResponse(
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
            tags=[TagInfo(id=tag.id, name=tag.name, color=tag.color) for tag in article.tags],
            html_path=article.html_path,
            processing_status=article.processing_status,
            original_html_url=article.original_html_url,
        )
        for article in articles
    ], total
