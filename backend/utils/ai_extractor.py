"""AI 提取工具：使用前端传入的智谱 API Key 提取文章信息。"""
import asyncio
import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional

import aiofiles
from bs4 import BeautifulSoup
from zai import ZhipuAiClient

from backend.settings.config import settings

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=2)
DEFAULT_ZHIPU_MODEL = "glm-4-flash"


async def _call_ai_api(prompt: str, api_key: Optional[str], model: str = DEFAULT_ZHIPU_MODEL) -> Dict:
    """调用智谱 Chat Completions，并返回模型文本内容。"""
    if not api_key:
        raise ValueError("使用智谱 AI 提取时必须在前端提供 API Key")

    selected_model = (model or DEFAULT_ZHIPU_MODEL).strip()
    try:
        client = ZhipuAiClient(api_key=api_key)
        response = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("智谱 API 响应内容为空")
        return {"content": content}
    except ValueError:
        raise
    except Exception as exc:
        logger.error("[AI Extractor] 智谱 API 调用失败: %s", exc, exc_info=True)
        raise ValueError(f"智谱 AI 调用失败: {exc}")


def _clean_text(text: str) -> str:
    """清理文本中的控制字符，避免 JSON 解析失败。"""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"[\u2000-\u200f\u2028-\u202e\u2060-\u206f\ufff9-\uffff]", "", text)
    return re.sub(r"[\u007f-\u009f]", "", text)


def _clean_json_strings(obj):
    """递归清理 JSON 对象中的字符串值。"""
    if isinstance(obj, str):
        return _clean_text(obj)
    if isinstance(obj, dict):
        return {key: _clean_json_strings(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_clean_json_strings(item) for item in obj]
    return obj


def _parse_json_response(result_text: str) -> Dict:
    """解析模型返回的 JSON，兼容被 Markdown 代码块包裹的情况。"""
    result_text = _clean_text(result_text).strip()
    if result_text.startswith("```json"):
        result_text = result_text[7:]
    if result_text.startswith("```"):
        result_text = result_text[3:]
    if result_text.endswith("```"):
        result_text = result_text[:-3]

    try:
        return _clean_json_strings(json.loads(result_text.strip()))
    except json.JSONDecodeError as exc:
        logger.error("[AI Extractor] JSON 解析失败: %s", exc)
        start = result_text.find("{")
        end = result_text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return _clean_json_strings(json.loads(_clean_text(result_text[start:end])))
            except json.JSONDecodeError:
                pass
        raise ValueError("JSON 解析失败")


async def extract_article_from_url(
    url: str,
    html_content: str,
    api_key: Optional[str] = None,
    model: str = DEFAULT_ZHIPU_MODEL,
) -> Dict:
    """从网页 URL 和 HTML 内容中提取标题、正文、摘要和关键词。"""
    html_content = _clean_text(html_content)
    prompt = f"""请从以下网页内容中提取文章信息，并只返回 JSON：
网页链接: {url}

网页内容:
{html_content[:15000]}

返回格式：
{{
  "title": "文章标题",
  "content": "完整正文内容，保留 Markdown 格式并去除无关内容",
  "summary": "文章摘要，100-200字",
  "keywords": "关键词,关键词,关键词"
}}"""

    result = await _call_ai_api(prompt=prompt, api_key=api_key, model=model)
    return _parse_json_response(result["content"].strip())


def _extract_article_summary_sync(
    content: str,
    api_key: Optional[str] = None,
    model: str = DEFAULT_ZHIPU_MODEL,
) -> Dict:
    """在线程池中同步提取摘要和关键词。"""
    prompt = f"""从以下文章内容提取摘要和关键词：

{_clean_text(content)}

只返回 JSON：{{"summary":"100-200字摘要","keywords":"关键词,关键词,关键词"}}"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_call_ai_api(prompt, api_key, model))
        return _parse_json_response(result["content"].strip())
    finally:
        loop.close()


async def extract_article_summary(
    content: str,
    api_key: Optional[str] = None,
    model: str = DEFAULT_ZHIPU_MODEL,
) -> Dict:
    """从已有文章内容中提取摘要和关键词。"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _extract_article_summary_sync, content, api_key, model)


async def extract_article_async(article_id: int) -> bool:
    """异步提取文章摘要和关键词；没有用户 API Key 时只记录失败状态。"""
    from backend.models import Article

    try:
        article = await Article.get(id=article_id)
        article.processing_status = "processing"
        await article.save()

        if not article.html_path:
            logger.warning("[AI Extractor] Article %s: No html_path", article_id)
            return False

        html_path = os.path.join(settings.upload_dir, article.html_path)
        if not os.path.exists(html_path):
            logger.warning("[AI Extractor] Article %s: File not found", article_id)
            return False

        async with aiofiles.open(html_path, "r", encoding="utf-8") as file:
            html_content = await file.read()

        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text_content = " ".join(soup.get_text(separator=" ", strip=True).split())[:5000]
        result = await extract_article_summary(text_content)
        article.summary = result.get("summary")
        article.keywords = result.get("keywords")
        article.processing_status = "completed"
        await article.save()
        return True
    except Exception as exc:
        logger.error("[AI Extractor] Article %s: Failed - %s", article_id, exc, exc_info=True)
        try:
            article = await Article.get(id=article_id)
            article.processing_status = "failed"
            await article.save()
        except Exception as status_exc:
            logger.error("[AI Extractor] Article %s: 状态更新失败 - %s", article_id, status_exc, exc_info=True)
        return False
