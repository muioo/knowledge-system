"""AI 提取工具 - 使用火山引擎大模型从网页内容提取文章信息"""
import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional

import httpx

from backend.settings.config import settings

# 创建线程池用于执行同步的 AI 调用
_executor = ThreadPoolExecutor(max_workers=2)

# 火山引擎 API 配置
ARK_API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
ARK_MODEL = "ep-20260302234602-pz4hc"


async def _call_ai_api(prompt: str, api_key: Optional[str] = None) -> Dict:
    """
    直接调用火山引擎 API（使用 HTTP 请求，无需 SDK）

    Args:
        prompt: 提示词
        api_key: API Key（可选，不提供则使用配置文件中的）

    Returns:
        AI 返回的解析结果

    Raises:
        ValueError: API 调用失败时抛出异常
    """
    # 使用传入的 API Key 或配置文件中的
    key = api_key or settings.ark_api_key
    if not key:
        raise ValueError("API Key 未配置，请在设置中配置 ARK_API_KEY 或在使用时提供 api_key 参数")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": ARK_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        timeout_config = httpx.Timeout(
            connect=10.0,
            read=60.0,
            write=10.0,
            pool=10.0
        )

        async with httpx.AsyncClient(
            timeout=timeout_config,
            verify=settings.verify_ssl,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            response = await client.post(
                f"{ARK_API_BASE}/chat/completions",
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return {"content": content}
            else:
                raise ValueError(f"API 响应格式异常")

    except httpx.HTTPStatusError as e:
        raise ValueError(f"API 请求失败 (HTTP {e.response.status_code})")
    except httpx.TimeoutException:
        raise ValueError("网络请求超时")
    except httpx.RequestError:
        raise ValueError("网络请求失败")
    except Exception as e:
        raise ValueError(f"AI 调用失败: {str(e)}")


def _clean_text(text: str) -> str:
    """清理文本中的控制字符"""
    import re

    # 移除 ASCII 控制字符（除了换行、制表符、回车）
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # 移除 Unicode 控制字符（零宽字符、不可见字符等）
    text = re.sub(r'[\u2000-\u200f\u2028-\u202e\u2060-\u206f\ufff9-\ufffb\ufffe-\uffff]', '', text)
    text = re.sub(r'[\u007f-\u009f]', '', text)

    return text


def _clean_json_strings(obj) -> Dict:
    """递归清理 JSON 对象中的所有字符串值"""
    if isinstance(obj, str):
        return _clean_text(obj)
    elif isinstance(obj, dict):
        return {k: _clean_json_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_clean_json_strings(item) for item in obj]
    else:
        return obj


def _parse_json_response(result_text: str) -> Dict:
    """解析 AI 返回的 JSON 结果"""
    import logging
    logger = logging.getLogger(__name__)

    result_text = _clean_text(result_text).strip()

    # 移除 markdown 代码块标记
    if result_text.startswith("```json"):
        result_text = result_text[7:]
    if result_text.startswith("```"):
        result_text = result_text[3:]
    if result_text.endswith("```"):
        result_text = result_text[:-3]
    result_text = result_text.strip()

    try:
        parsed = json.loads(result_text)
        parsed = _clean_json_strings(parsed)
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"[AI Extractor] JSON 解析失败: {str(e)}")

        # 尝试提取 JSON 部分
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = result_text[start:end]
            json_str = _clean_text(json_str)
            try:
                parsed = json.loads(json_str)
                parsed = _clean_json_strings(parsed)
                return parsed
            except json.JSONDecodeError:
                pass

        raise ValueError(f"JSON解析失败")


async def extract_article_from_url(url: str, html_content: str, api_key: Optional[str] = None) -> Dict:
    """
    从网页 URL 和内容中提取文章信息

    Args:
        url: 文章链接
        html_content: 网页内容
        api_key: 火山引擎 ARK API Key（可选，不提供则使用配置文件中的）

    Returns:
        包含 title, content, summary, keywords 的字典
    """
    html_content = _clean_text(html_content)

    prompt = f"""请从以下网页内容中提取文章信息，以JSON格式返回：

网页链接: {url}

网页内容:
{html_content[:15000]}

请提取以下信息并以JSON格式返回：
{{
    "title": "文章标题",
    "content": "完整正文内容（保留Markdown格式，去除无关内容）",
    "summary": "文章摘要（100-200字）",
    "keywords": "关键词1,关键词2,关键词3"
}}

只返回JSON，不要其他内容。"""

    try:
        result = await _call_ai_api(prompt, api_key)
        result_text = result["content"].strip()
        return _parse_json_response(result_text)
    except Exception as e:
        raise ValueError(f"AI 提取失败: {str(e)}")


def _extract_article_summary_sync(content: str, api_key: Optional[str] = None) -> Dict:
    """同步版本的摘要提取（在线程池中运行）"""
    import asyncio

    content = _clean_text(content)

    prompt = f"""从以下文章内容提取摘要和关键词：

{content}

返回JSON格式：
{{"summary":"100-200字摘要","keywords":"关键词1,关键词2,关键词3"}}"""

    # 在新的事件循环中运行异步函数
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_call_ai_api(prompt, api_key))
        result_text = result["content"].strip()
        return _parse_json_response(result_text)
    finally:
        loop.close()


async def extract_article_summary(content: str, api_key: Optional[str] = None) -> Dict:
    """
    从已有内容中提取摘要和关键词

    Args:
        content: 文章内容
        api_key: API Key（可选）

    Returns:
        包含 summary, keywords 的字典
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _extract_article_summary_sync, content, api_key)


async def extract_article_async(article_id: int) -> bool:
    """
    异步提取文章摘要和关键词（用于后台任务）

    Returns:
        bool: 成功返回 True，失败返回 False
    """
    import logging
    import aiofiles
    from backend.models import Article

    logger = logging.getLogger(__name__)

    try:
        article = await Article.get(id=article_id)
        article.processing_status = "processing"
        await article.save()

        if not article.html_path:
            logger.warning(f"[AI Extractor] Article {article_id}: No html_path")
            return False

        html_path = os.path.join(settings.upload_dir, article.html_path)

        if not os.path.exists(html_path):
            logger.warning(f"[AI Extractor] Article {article_id}: File not found")
            return False

        async with aiofiles.open(html_path, 'r', encoding='utf-8') as f:
            html_content = await f.read()

        # 提取正文内容
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        text_content = soup.get_text(separator=' ', strip=True)
        text_content = ' '.join(text_content.split())[:5000]

        result = await extract_article_summary(text_content)

        article.summary = result.get("summary")
        article.keywords = result.get("keywords")
        article.processing_status = "completed"
        await article.save()

        logger.info(f"[AI Extractor] Article {article_id}: Successfully extracted")
        return True

    except Exception as e:
        logger.error(f"[AI Extractor] Article {article_id}: Failed - {str(e)}")

        try:
            article = await Article.get(id=article_id)
            article.processing_status = "failed"
            await article.save()
        except Exception:
            pass
        return False
