"""图片处理工具 - 提取、下载和重写 HTML 中的图片链接"""
import asyncio
import logging
import os
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin

import aiofiles
import httpx
from bs4 import BeautifulSoup

from backend.utils.html_fetcher import DEFAULT_HEADERS, is_valid_url
from backend.settings.config import settings

logger = logging.getLogger(__name__)

# 最大文件大小限制（10MB）
MAX_IMAGE_SIZE = 10 * 1024 * 1024

# 下载超时设置（秒）
DOWNLOAD_TIMEOUT = 30

# 最大重试次数
MAX_RETRIES = 3


def extract_images(html: str, base_url: Optional[str] = None) -> List[str]:
    """
    提取 HTML 中所有图片 URL（去重），支持处理相对路径

    Args:
        html: HTML 内容
        base_url: 基础URL，用于处理相对路径

    Returns:
        去重后的图片 URL 列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')

    urls = []
    seen = set()

    for img in img_tags:
        # 尝试从多个属性获取图片URL
        src = img.get('src') or img.get('data-src') or img.get('data-original')

        if not src:
            continue

        # 跳过 data URL
        if src.startswith('data:'):
            continue

        # 处理相对路径
        if base_url and not src.startswith(('http://', 'https://', '//')):
            try:
                src = urljoin(base_url, src)
            except Exception:
                continue

        # 验证URL有效性
        if is_valid_url(src) and src not in seen:
            urls.append(src)
            seen.add(src)

    logger.info(f"[Image Processor] 提取到 {len(urls)} 个唯一图片URL")
    return urls


async def download_image(url: str, save_path: str) -> bool:
    """
    下载单张图片（带重试机制）

    Args:
        url: 图片 URL
        save_path: 保存路径

    Returns:
        下载成功返回 True，失败返回 False
    """
    # URL 验证
    if not is_valid_url(url):
        return False

    # 重试机制
    for attempt in range(MAX_RETRIES):
        try:
            timeout_config = httpx.Timeout(
                connect=10.0,
                read=DOWNLOAD_TIMEOUT,
                write=10.0,
                pool=10.0
            )

            async with httpx.AsyncClient(
                timeout=timeout_config,
                verify=settings.verify_ssl,
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=20)
            ) as client:
                response = await client.get(url, headers=DEFAULT_HEADERS)
                response.raise_for_status()

                # 文件大小限制检查
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > MAX_IMAGE_SIZE:
                    logger.warning(f"[Image Processor] 图片过大: {url}")
                    return False

                content = response.content
                if len(content) > MAX_IMAGE_SIZE:
                    logger.warning(f"[Image Processor] 图片过大: {url}")
                    return False

                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                # 异步写入文件
                async with aiofiles.open(save_path, 'wb') as f:
                    await f.write(content)

                return True

        except httpx.TimeoutException:
            if attempt < MAX_RETRIES - 1:
                logger.debug(f"[Image Processor] 下载超时，重试 {attempt + 1}/{MAX_RETRIES}: {url}")
                await asyncio.sleep(1)
                continue
            else:
                logger.error(f"[Image Processor] 下载超时: {url}")
                return False

        except httpx.HTTPStatusError as e:
            logger.error(f"[Image Processor] HTTP错误 {e.response.status_code}: {url}")
            return False

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.debug(f"[Image Processor] 下载失败，重试 {attempt + 1}/{MAX_RETRIES}: {url}")
                await asyncio.sleep(1)
                continue
            else:
                logger.error(f"[Image Processor] 下载失败: {url} - {type(e).__name__}")
                return False

    return False


async def download_images_batch(urls: List[str], base_dir: str) -> Dict[str, str]:
    """
    批量下载图片

    Args:
        urls: 图片 URL 列表
        base_dir: 基础目录（图片将保存到 base_dir/images/ 子目录）

    Returns:
        {原始 URL: 本地路径/原始 URL} 映射
        下载成功则映射到本地路径，失败则保持原始 URL
    """
    if not urls:
        return {}

    logger.info(f"[Image Processor] 开始下载 {len(urls)} 张图片")

    # 创建图片保存目录
    images_dir = os.path.join(base_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    # 并发控制：最多 15 个并发下载
    semaphore = asyncio.Semaphore(15)

    async def download_with_semaphore(index: int, url: str) -> tuple:
        async with semaphore:
            # 获取文件扩展名
            parsed_url = urlparse(url)
            ext = os.path.splitext(parsed_url.path)[1]

            # 如果没有扩展名，尝试从URL参数中获取
            if not ext:
                # 尝试从查询参数中获取格式
                query_params = parsed_url.query.split('&')
                for param in query_params:
                    if 'format=' in param:
                        ext = '.' + param.split('=')[1]
                        break

            # 默认扩展名
            if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']:
                ext = '.jpg'

            # 生成文件名
            filename = f"img_{index:04d}{ext}"
            save_path = os.path.join(images_dir, filename)

            # 下载图片
            success = await download_image(url, save_path)

            if success:
                # 返回相对路径
                relative_path = os.path.join('images', filename).replace('\\', '/')
                return (url, relative_path)
            else:
                # 失败则保持原始 URL
                return (url, url)

    # 创建下载任务
    tasks = [download_with_semaphore(i, url) for i, url in enumerate(urls, start=1)]

    # 并发执行所有下载任务
    results = await asyncio.gather(*tasks, return_exceptions=False)

    # 构建映射字典
    mapping = dict(results)

    # 统计结果
    success_count = sum(1 for url, path in mapping.items() if path != url and not path.startswith('http'))
    failed_count = len(urls) - success_count

    if success_count > 0:
        logger.info(f"[Image Processor] 下载完成: {success_count} 成功, {failed_count} 失败")
    elif failed_count > 0:
        logger.warning(f"[Image Processor] 所有图片下载失败 ({failed_count} 张)")

    return mapping


def rewrite_image_links(html: str, url_mapping: Dict[str, str]) -> str:
    """
    重写 HTML 中的图片链接

    Args:
        html: HTML 内容
        url_mapping: {原始 URL: 本地路径/原始 URL} 映射

    Returns:
        重写后的 HTML 内容
        下载失败的图片会添加 data-download-failed="true" 属性
    """
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')

    rewritten_count = 0

    for img in img_tags:
        # 尝试从多个属性获取原始URL
        original_src = (img.get('src') or
                       img.get('data-src') or
                       img.get('data-original'))

        if not original_src:
            continue

        # 跳过 data URL
        if original_src.startswith('data:'):
            continue

        # 检查是否在映射中
        if original_src in url_mapping:
            new_src = url_mapping[original_src]

            # 只更新成功下载的图片
            if new_src != original_src and not new_src.startswith('http'):
                img['src'] = new_src
                rewritten_count += 1

                # 清理data-src等属性，避免干扰
                if img.get('data-src'):
                    del img['data-src']
                if img.get('data-original'):
                    del img['data-original']
            else:
                # 下载失败
                img['data-download-failed'] = 'true'

    if rewritten_count > 0:
        logger.info(f"[Image Processor] 重写了 {rewritten_count} 个图片链接")

    return str(soup)
