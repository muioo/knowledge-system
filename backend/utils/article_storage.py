import os
import shutil
from typing import Optional
from pathlib import Path

import aiofiles

from backend.settings.config import settings


def get_article_dir(article_id: int) -> str:
    """获取文章存储目录路径"""
    return os.path.join(settings.upload_dir, "articles", str(article_id))


def get_html_path(article_id: int) -> str:
    """获取 HTML 文件路径"""
    return os.path.join(get_article_dir(article_id), "index.html")


def get_relative_html_path(article_id: int) -> str:
    """获取 HTML 文件相对路径（用于存储到数据库）"""
    return f"articles/{article_id}/index.html"


async def ensure_article_dir(article_id: int) -> str:
    """确保文章目录存在"""
    article_dir = get_article_dir(article_id)
    os.makedirs(article_dir, exist_ok=True)
    return article_dir


async def save_html_content(article_id: int, html_content: str) -> str:
    """
    保存 HTML 内容到文件

    Returns:
        相对路径
    """
    await ensure_article_dir(article_id)

    html_path = get_html_path(article_id)
    async with aiofiles.open(html_path, "w", encoding="utf-8") as f:
        await f.write(html_content)

    return get_relative_html_path(article_id)


async def read_html_content(article_id: int) -> str:
    """
    读取 HTML 文件内容

    Raises:
        FileNotFoundError: 文件不存在
    """
    html_path = get_html_path(article_id)

    if not os.path.exists(html_path):
        raise FileNotFoundError(f"文章内容文件不存在: {html_path}")

    async with aiofiles.open(html_path, "r", encoding="utf-8") as f:
        return await f.read()


async def delete_article_files(article_id: int) -> None:
    """删除文章相关文件"""
    article_dir = get_article_dir(article_id)

    if os.path.exists(article_dir):
        shutil.rmtree(article_dir)


async def get_article_file_content(article_id: int, html_path: Optional[str], original_filename: Optional[str]) -> str:
    """
    根据文章信息获取文件内容

    优先使用 html_path（URL 导入），否则使用 original_filename（本地上传）

    Args:
        article_id: 文章 ID
        html_path: HTML 文件相对路径
        original_filename: 原始文件名

    Returns:
        文件内容

    Raises:
        FileNotFoundError: 文件不存在
    """
    # URL 导入：使用 html_path
    if html_path:
        full_path = os.path.join(settings.upload_dir, html_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"文章文件不存在: {html_path}")
        async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
            return await f.read()

    # 本地上传：使用 id + original_filename
    elif original_filename:
        file_path = os.path.join(
            settings.upload_dir,
            "articles",
            str(article_id),
            original_filename
        )
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文章文件不存在: {original_filename}")
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.read()

    else:
        raise FileNotFoundError("文章文件不存在")
