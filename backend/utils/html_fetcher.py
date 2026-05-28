"""HTML 获取和处理工具模块。"""
import logging
import os
from typing import Tuple
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

try:
    from readability import Document
except ImportError:
    Document = None

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
}


def is_valid_url(url: str) -> bool:
    """验证 URL 是否为 http/https 地址。"""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    return bool(url) and (url.startswith("http://") or url.startswith("https://"))


def build_request_headers(url: str) -> dict:
    """按站点生成请求头，知乎可通过 ZHIHU_COOKIE 提供登录 Cookie。"""
    headers = dict(DEFAULT_HEADERS)
    hostname = urlparse(url).netloc.lower()
    if "zhihu.com" in hostname:
        headers["Referer"] = "https://www.zhihu.com/"
        cookie = os.getenv("ZHIHU_COOKIE", "").strip()
        if cookie:
            headers["Cookie"] = cookie
    elif "mp.weixin.qq.com" in hostname:
        headers["Referer"] = "https://mp.weixin.qq.com/"
    return headers


async def fetch_html(url: str) -> str:
    """获取网页原始 HTML。"""
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")

    timeout = httpx.Timeout(30.0, connect=10.0)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=build_request_headers(url))
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as exc:
            logger.error("[HTML Fetcher] 获取页面失败: %s HTTP %s", url, exc.response.status_code)
            if exc.response.status_code == 403 and "zhihu.com" in url:
                raise ValueError("知乎返回 403 风控页，请配置 ZHIHU_COOKIE 后重试")
            if exc.response.status_code == 403:
                raise ValueError("访问被拒绝(403)，该网站禁止程序访问")
            if exc.response.status_code == 404:
                raise ValueError(f"页面不存在: {url}")
            raise ValueError(f"获取页面失败 (HTTP {exc.response.status_code}): {exc}")
        except httpx.RequestError as exc:
            logger.error("[HTML Fetcher] 网络请求失败: %s %s", url, exc)
            raise ValueError(f"网络请求失败: {exc}")


def clean_html(html: str, url: str = "") -> Tuple[str, str]:
    """清洗 HTML 并返回正文 HTML 与标题。"""
    hostname = urlparse(url).netloc.lower() if url else ""
    if "mp.weixin.qq.com" in hostname:
        return _clean_wechat_article(html)

    if Document is not None:
        doc = Document(html)
        return doc.summary(), doc.title()

    logger.warning("[HTML Fetcher] readability 未安装，使用 BeautifulSoup 降级清洗")
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else "未命名文章"
    return str(soup.body or soup), title


def _clean_wechat_article(html: str) -> Tuple[str, str]:
    """提取微信公众号文章结构，并恢复 data-src 图片。"""
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("#js_content")
    title_node = soup.select_one("#activity-name")
    author_node = soup.select_one("#js_name")
    if content is None:
        logger.warning("[HTML Fetcher] 微信文章缺少 #js_content，降级到通用清洗")
        return _clean_with_readability_or_soup(html)

    for img in content.select("img[data-src]"):
        img["src"] = img.get("data-src", "")
    for tag in content(["script", "style"]):
        tag.decompose()

    title = title_node.get_text(strip=True) if title_node else "未命名文章"
    author = author_node.get_text(strip=True) if author_node else ""
    if not author:
        return str(content), title

    wrapper = soup.new_tag("div")
    meta = soup.new_tag("p")
    meta.string = f"来源：{author}"
    wrapper.append(meta)
    wrapper.append(content)
    return str(wrapper), title


def _clean_with_readability_or_soup(html: str) -> Tuple[str, str]:
    """优先使用 readability，缺失时降级到 BeautifulSoup。"""
    if Document is not None:
        doc = Document(html)
        return doc.summary(), doc.title()
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else "未命名文章"
    return str(soup.body or soup), title


def remove_scripts(html: str) -> str:
    """移除脚本、meta refresh 和 iframe。"""
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script"):
        script.decompose()
    for meta in soup.find_all("meta", attrs={"http-equiv": lambda value: value and "refresh" in value.lower()}):
        meta.decompose()
    for iframe in soup.find_all("iframe"):
        iframe.decompose()
    return str(soup)


async def rewrite_base_urls(html: str, base_url: str) -> str:
    """将 HTML 中图片相对路径转为绝对路径。"""
    soup = BeautifulSoup(html, "html.parser")
    for img in soup.find_all("img", src=True):
        img["src"] = urljoin(base_url, img["src"])
    return str(soup)
