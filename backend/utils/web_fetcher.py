"""网页内容获取工具"""
import httpx
from typing import Optional
from html2text import HTML2Text
from bs4 import BeautifulSoup


async def fetch_web_content(url: str) -> dict:
    """
    获取网页内容并转换为 Markdown

    Args:
        url: 网页链接

    Returns:
        包含 title, content, html 的字典
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        html = response.text

        # 使用 BeautifulSoup 解析标题
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        title = title.get_text().strip() if title else "未命名文章"

        # 使用 html2text 转换为 Markdown
        h = HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # 不自动换行
        markdown_content = h.handle(html)

        return {
            "title": title,
            "content": markdown_content,
            "html": html
        }


async def fetch_web_content_simple(url: str) -> str:
    """
    简单获取网页内容（返回原始 HTML）

    Args:
        url: 网页链接

    Returns:
        HTML 内容
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text
