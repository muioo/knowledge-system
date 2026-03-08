"""网页内容获取工具"""
import httpx
from typing import Optional
from html2text import HTML2Text
from bs4 import BeautifulSoup


# 简化的浏览器请求头
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


async def fetch_web_content(url: str) -> dict:
    """
    获取网页内容并转换为 Markdown

    Args:
        url: 网页链接

    Returns:
        包含 title, content, html 的字典
    """
    timeout = httpx.Timeout(30.0, connect=10.0)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)

    async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=BROWSER_HEADERS)
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
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise ValueError(f"访问被拒绝 (403)，该网站禁止程序访问。建议：1) 使用其他网站 2) 手动复制网页内容后使用文件上传功能")
            elif e.response.status_code == 404:
                raise ValueError(f"页面不存在: {url}")
            else:
                raise ValueError(f"获取页面失败 (HTTP {e.response.status_code}): {str(e)}")
        except httpx.RequestError as e:
            raise ValueError(f"网络请求失败: {str(e)}")


async def fetch_web_content_simple(url: str) -> str:
    """
    简单获取网页内容（返回原始 HTML）

    Args:
        url: 网页链接

    Returns:
        HTML 内容
    """
    timeout = httpx.Timeout(30.0, connect=10.0)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)

    async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=BROWSER_HEADERS)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise ValueError(f"访问被拒绝 (403)，该网站禁止程序访问。建议：1) 使用其他网站 2) 手动复制网页内容后使用文件上传功能")
            elif e.response.status_code == 404:
                raise ValueError(f"页面不存在: {url}")
            else:
                raise ValueError(f"获取页面失败 (HTTP {e.response.status_code}): {str(e)}")
        except httpx.RequestError as e:
            raise ValueError(f"网络请求失败: {str(e)}")
