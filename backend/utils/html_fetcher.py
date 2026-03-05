"""HTML 获取和处理工具模块"""
from typing import Tuple
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from readability import Document


async def fetch_html(url: str) -> str:
    """
    获取网页原始 HTML

    Args:
        url: 要获取的网页 URL

    Returns:
        str: 网页的原始 HTML 内容

    Raises:
        httpx.HTTPError: 当请求失败时抛出
    """
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def clean_html(html: str) -> Tuple[str, str]:
    """
    使用 readability 清洗 HTML

    Args:
        html: 原始 HTML 内容

    Returns:
        Tuple[str, str]: (清洗后的 HTML, 标题)
    """
    doc = Document(html)
    return doc.summary(), doc.title()


async def rewrite_base_urls(html: str, base_url: str) -> str:
    """
    将相对路径转换为绝对路径（只处理 img 标签）

    Args:
        html: HTML 内容
        base_url: 基础 URL，用于解析相对路径

    Returns:
        str: 处理后的 HTML 内容
    """
    soup = BeautifulSoup(html, "html.parser")

    for img in soup.find_all("img", src=True):
        img["src"] = urljoin(base_url, img["src"])

    return str(soup)
