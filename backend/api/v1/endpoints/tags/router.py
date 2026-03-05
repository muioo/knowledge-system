from fastapi import APIRouter, HTTPException, Depends
from backend.core.security import get_current_user
from backend.models import User
from backend.schemas.response import SuccessResponse
from backend.controllers.tag_controller import (
    create_tag,
    get_tag_by_id,
    list_tags,
    update_tag,
    delete_tag,
    get_articles_by_tag
)
from schemas.article import ArticleResponse
from schemas.response import PaginatedResponse, PaginatedData

router = APIRouter(prefix="/tags", tags=["标签"])

@router.get("/", response_model=SuccessResponse[list])
async def get_tags():
    tags = await list_tags()
    return SuccessResponse(data=tags)

@router.get("/{tag_id}", response_model=SuccessResponse[TagResponse])
async def get_tag(tag_id: int):
    try:
        result = await get_tag_by_id(tag_id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=SuccessResponse[TagResponse])
async def create_new_tag(
    data: TagCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await create_tag(data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{tag_id}", response_model=SuccessResponse[TagResponse])
async def update_tag_by_id(
    tag_id: int,
    data: TagUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await update_tag(tag_id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{tag_id}", status_code=204)
async def delete_tag_by_id(
    tag_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        await delete_tag(tag_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{tag_id}/articles", response_model=PaginatedResponse[ArticleResponse])
async def get_tag_articles(
    tag_id: int,
    page: int = 1,
    size: int = 20
):
    try:
        articles, total = await get_articles_by_tag(tag_id, page, size)
        return PaginatedResponse(data=PaginatedData(
            total=total,
            page=page,
            size=size,
            items=articles
        ))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
