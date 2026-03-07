from fastapi import APIRouter, Depends, Query
from typing import Optional
from backend.core.security import get_current_user
from backend.models import User
from backend.schemas.article import ArticleResponse
from backend.schemas.response import PaginatedResponse, PaginatedData
from backend.controllers.article_controller import search_articles

router = APIRouter(prefix="/search", tags=["搜索"])

@router.get("/articles", response_model=PaginatedResponse[ArticleResponse])
async def search_articles_endpoint(
    q: Optional[str] = None,
    tags: Optional[str] = Query(None, description="逗号分隔的标签ID"),
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    tag_ids = [int(t) for t in tags.split(",")] if tags else None

    from backend.schemas.article import SearchQuery
    query = SearchQuery(q=q, tags=tag_ids, page=page, size=size)

    articles, total = await search_articles(query)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=articles
    ))
