"""图片处理工具 - 提取、下载和重写 HTML 中的图片链接"""
import asyncio
import os
from typing import Dict, List
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


async def extract_images(html: str) -> List[str]:
    """
    提取 HTML 中所有图片 URL（去重）

    Args:
        html: HTML 内容

    Returns:
        去重后的图片 URL 列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')

    urls = []
    seen = set()

    for img in img_tags:
        src = img.get('src')
        if src and src not in seen:
            urls.append(src)
            seen.add(src)

    return urls


async def download_image(url: str, save_path: str) -> bool:
    """
    下载单张图片

    Args:
        url: 图片 URL
        save_path: 保存路径

    Returns:
        下载成功返回 True，失败返回 False
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 写入文件
            with open(save_path, 'wb') as f:
                f.write(response.content)

            return True
    except Exception:
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

    # 创建图片保存目录
    images_dir = os.path.join(base_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    # 并发控制：最多 10 个并发下载
    semaphore = asyncio.Semaphore(10)

    async def download_with_semaphore(index: int, url: str) -> tuple:
        async with semaphore:
            # 获取文件扩展名
            parsed_url = urlparse(url)
            ext = os.path.splitext(parsed_url.path)[1]
            if not ext:
                ext = '.jpg'  # 默认扩展名

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
    results = await asyncio.gather(*tasks)

    # 构建映射字典
    return dict(results)


async def rewrite_image_links(html: str, url_mapping: Dict[str, str]) -> str:
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

    for img in img_tags:
        original_src = img.get('src')
        if not original_src:
            continue

        # 检查是否在映射中
        if original_src in url_mapping:
            new_src = url_mapping[original_src]
            img['src'] = new_src

            # 如果新 URL 与原始 URL 相同，说明下载失败
            if new_src == original_src:
                img['data-download-failed'] = 'true'

    return str(soup)
