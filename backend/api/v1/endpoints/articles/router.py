from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from typing import Optional
from backend.core.security import get_current_user, get_current_admin
from backend.models import User
from backend.schemas.article import (
    ArticleUpdate,
    ArticleResponse,
    ArticleFromHtmlUrlRequest,
    ArticleFromHtmlUrlResponse,
    ArticleHtmlResponse
)
from backend.schemas.response import SuccessResponse, PaginatedResponse, PaginatedData
from backend.controllers.article_controller import (
    create_article_from_file,
    get_article_by_id,
    update_article,
    delete_article,
    list_articles,
    import_article_from_html_url,
    get_article_html_content
)
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
            except Exception:
                pass  # HTML 读取失败不影响基本信息返回

        # 组合响应
        response_data = ArticleHtmlResponse(
            **result.model_dump(),
            html_content=html_content
        )

        return SuccessResponse(data=response_data)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/upload", response_model=SuccessResponse[ArticleResponse])
async def upload_file_to_create_article(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None),
    tag_ids: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    上传本地文件创建文章

    - 保存原文件到 articles/{article_id}/ 目录
    - 转换为 markdown 存入 content 字段
    - 支持手动填写标题、摘要、关键词、标签
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


async def run_ai_extraction(article_id: int):
    """后台任务：执行 AI 提取"""
    from backend.utils.ai_extractor import extract_article_async
    await extract_article_async(article_id)


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
