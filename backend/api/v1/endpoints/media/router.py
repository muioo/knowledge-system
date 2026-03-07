"""媒体文件访问端点 - 提供文章图片等静态资源访问"""
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

from backend.settings.config import settings

router = APIRouter(prefix="/media", tags=["媒体文件"])


@router.get("/articles/{article_id}/{file_path:path}")
async def get_article_media(
    article_id: int,
    file_path: str
):
    """
    获取文章的媒体文件（图片等）

    注意：此端点不需要认证，因为HTML中的img标签无法携带认证头
    安全性：文件路径有严格验证，只能访问uploads目录下的文件

    Args:
        article_id: 文章ID
        file_path: 文件相对路径（如 images/img_0001.jpg 或 index.html）

    Returns:
        文件响应

    Raises:
        HTTPException: 文件不存在或无权访问
    """
    # 构建文件路径
    # file_path 可能是 "images/img_0001.jpg" 或 "index.html"
    article_dir = os.path.join(settings.upload_dir, "articles", str(article_id))
    full_path = os.path.join(article_dir, file_path)

    # 安全检查：确保路径在文章目录内
    try:
        resolved_path = Path(full_path).resolve()
        resolved_article_dir = Path(article_dir).resolve()

        # 确保解析后的路径在文章目录内
        if not str(resolved_path).startswith(str(resolved_article_dir)):
            raise HTTPException(status_code=403, detail="无权访问此文件")

    except Exception:
        raise HTTPException(status_code=403, detail="无效的文件路径")

    # 检查文件是否存在
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    if not os.path.isfile(full_path):
        raise HTTPException(status_code=400, detail="不是有效的文件")

    # 根据文件扩展名确定媒体类型
    media_type = _get_media_type(full_path)

    # 返回文件
    return FileResponse(
        full_path,
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=31536000",  # 缓存一年
            "Content-Disposition": "inline"  # 内联显示，不下载
        }
    )


def _get_media_type(file_path: str) -> str:
    """
    根据文件扩展名获取媒体类型

    Args:
        file_path: 文件路径

    Returns:
        媒体类型字符串
    """
    ext = os.path.splitext(file_path)[1].lower()

    media_types = {
        # 图片
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.bmp': 'image/bmp',
        # HTML
        '.html': 'text/html',
        '.htm': 'text/html',
        # 文本
        '.txt': 'text/plain',
        '.css': 'text/css',
        '.js': 'application/javascript',
        # PDF
        '.pdf': 'application/pdf',
    }

    return media_types.get(ext, 'application/octet-stream')
