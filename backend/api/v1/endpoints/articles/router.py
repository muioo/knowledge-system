from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
from backend.core.security import get_current_user, get_current_admin
from backend.models import User
from backend.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from backend.schemas.response import SuccessResponse, PaginatedResponse, PaginatedData
from backend.controllers.article_controller import (
    create_article,
    get_article_by_id,
    update_article,
    delete_article,
    list_articles
)
from backend.utils.converters import convert_document
import aiofiles
import os
from backend.settings.config import settings

router = APIRouter(prefix="/articles", tags=["文章"])

@router.get("/", response_model=PaginatedResponse[ArticleResponse])
async def get_articles(
    page: int = 1,
    size: int = 20,
    tag_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    articles, total = await list_articles(page, size, tag_id)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=articles
    ))

@router.get("/{article_id}", response_model=SuccessResponse[ArticleResponse])
async def get_article(
    article_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await get_article_by_id(article_id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=SuccessResponse[ArticleResponse])
async def create_new_article(
    data: ArticleCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await create_article(data, current_user.id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{article_id}", response_model=SuccessResponse[ArticleResponse])
async def update_article_by_id(
    article_id: int,
    data: ArticleUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        is_admin = current_user.role == "admin"
        result = await update_article(article_id, data, current_user.id, is_admin)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400 if "无权" in str(e) else 404, detail=str(e))

@router.delete("/{article_id}", status_code=204)
async def delete_article_by_id(
    article_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        is_admin = current_user.role == "admin"
        await delete_article(article_id, current_user.id, is_admin)
    except ValueError as e:
        raise HTTPException(status_code=403 if "无权" in str(e) else 404, detail=str(e))

@router.post("/upload", response_model=SuccessResponse[ArticleResponse])
async def upload_document(
    file: UploadFile = File(...),
    tag_ids: str = Form(None),
    current_user: User = Depends(get_current_user)
):
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(status_code=413, detail="文件过大")

    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, file.filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    try:
        markdown_content, title = await convert_document(file_path, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))

    tag_id_list = [int(t) for t in tag_ids.split(",")] if tag_ids else []
    article_data = ArticleCreate(
        title=title,
        content=markdown_content,
        tag_ids=tag_id_list
    )

    try:
        result = await create_article(article_data, current_user.id)
        from models import Article
        article = await Article.get(id=result.id)
        article.original_filename = file.filename
        await article.save()
        result.original_filename = file.filename
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
