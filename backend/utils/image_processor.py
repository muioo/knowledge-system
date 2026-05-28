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


def extract_images(html: str, base_url: Optional[str] = None, include_local_paths: bool = False) -> tuple[List[str], List[str]]:
    """
    提取 HTML 中所有图片 URL（去重），支持处理相对路径

    Args:
        html: HTML 内容
        base_url: 基础URL，用于处理相对路径
        include_local_paths: 是否包含本地路径图片（非 http/https URL）

    Returns:
        (网络图片URL列表, 本地路径图片列表) 元组
    """
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')

    network_urls = []
    local_paths = []
    seen_network = set()
    seen_local = set()

    for img in img_tags:
        # 尝试从多个属性获取图片URL
        src = img.get('src') or img.get('data-src') or img.get('data-original')

        if not src:
            continue

        # 跳过 data URL
        if src.startswith('data:'):
            continue

        # 判断是否为网络 URL
        is_network = src.startswith(('http://', 'https://'))

        if is_network:
            # 网络图片：去重后添加
            if src not in seen_network:
                network_urls.append(src)
                seen_network.add(src)
        elif include_local_paths:
            # 本地路径图片：去重后添加
            if src not in seen_local:
                local_paths.append(src)
                seen_local.add(src)

    logger.info(f"[Image Processor] 提取到 {len(network_urls)} 个网络图片, {len(local_paths)} 个本地路径图片")
    return network_urls, local_paths


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


def rewrite_image_links(html: str, url_mapping: Dict[str, str], local_paths: Optional[List[str]] = None, remove_local_images: bool = False) -> str:
    """
    重写 HTML 中的图片链接

    Args:
        html: HTML 内容
        url_mapping: {原始 URL/路径: 本地路径} 映射（包含网络图片和已上传的本地图片）
        local_paths: 本地路径图片列表（用于识别哪些是本地路径）
        remove_local_images: 是否移除未映射的本地路径图片标签

    Returns:
        重写后的 HTML 内容
        - 在映射中的图片（网络或本地）：替换为新的本地路径
        - 未映射的网络图片：添加 data-download-failed="true" 属性
        - 未映射的本地路径图片：
            - remove_local_images=True: 移除图片标签
            - remove_local_images=False: 添加 data-local-path="true" 属性
    """
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')

    rewritten_count = 0
    removed_local_count = 0
    marked_local_count = 0

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

        # 检查是否在映射中（无论网络还是本地路径）
        if original_src in url_mapping:
            new_src = url_mapping[original_src]

            # 替换为新的本地路径
            if new_src != original_src:
                img['src'] = new_src
                rewritten_count += 1

                # 清理data-src等属性，避免干扰
                if img.get('data-src'):
                    del img['data-src']
                if img.get('data-original'):
                    del img['data-original']
            continue

        # 判断是否为网络 URL
        is_network_url = original_src.startswith(('http://', 'https://'))

        if is_network_url:
            # 网络图片但未在映射中（下载失败）
            img['data-download-failed'] = 'true'
        else:
            # 本地路径图片且未在映射中（没有上传对应的文件）
            if remove_local_images:
                # 移除图片标签
                img.decompose()
                removed_local_count += 1
            else:
                # 标记但保持原样
                if not img.get('data-local-path'):
                    img['data-local-path'] = 'true'
                    img['alt'] = img.get('alt', '本地图片（未上传）')
                    marked_local_count += 1

    if rewritten_count > 0:
        logger.info(f"[Image Processor] 重写了 {rewritten_count} 个图片链接")
    if removed_local_count > 0:
        logger.info(f"[Image Processor] 移除了 {removed_local_count} 个本地路径图片标签（未上传）")
    if marked_local_count > 0:
        logger.info(f"[Image Processor] 标记了 {marked_local_count} 个本地路径图片（未上传）")

    return str(soup)
