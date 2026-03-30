"""HTML 获取和处理工具模块"""
from typing import Tuple
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from readability import Document


# 默认 User-Agent 头，模拟浏览器访问（简化版，更像真实浏览器）
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def is_valid_url(url: str) -> bool:
    """
    验证 URL 格式是否有效

    Args:
        url: 要验证的 URL

    Returns:
        bool: URL 是否有效
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if not url:
        return False

    # 检查是否以 http:// 或 https:// 开头
    if not (url.startswith("http://") or url.startswith("https://")):
        return False

    return True


async def fetch_html(url: str) -> str:
    """
    获取网页原始 HTML

    Args:
        url: 要获取的网页 URL

    Returns:
        str: 网页的原始 HTML 内容

    Raises:
        ValueError: 当 URL 格式无效时抛出
        httpx.HTTPError: 当请求失败时抛出
    """
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")

    # 配置请求参数
    timeout = httpx.Timeout(30.0, connect=10.0)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)

    async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=DEFAULT_HEADERS)
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


def remove_scripts(html: str) -> str:
    """
    移除 HTML 中的所有脚本和可能导致跳转的元素

    Args:
        html: 原始 HTML 内容

    Returns:
        str: 移除脚本后的 HTML 内容
    """
    soup = BeautifulSoup(html, 'html.parser')

    # 移除所有 script 标签
    for script in soup.find_all('script'):
        script.decompose()

    # 移除 meta refresh 跳转
    for meta in soup.find_all('meta', attrs={'http-equiv': lambda x: x and 'refresh' in x.lower()}):
        meta.decompose()

    # 移除 iframe（可能包含跳转）
    for iframe in soup.find_all('iframe'):
        iframe.decompose()

    return str(soup)


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
