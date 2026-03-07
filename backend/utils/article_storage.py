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
