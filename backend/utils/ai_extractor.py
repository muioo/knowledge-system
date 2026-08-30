"""AI 提取工具：支持智谱 SDK 专路与千问/自定义 OpenAI 兼容协议。密钥均仅来自后端环境变量。"""
import asyncio
import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional

import aiofiles
from bs4 import BeautifulSoup
from openai import OpenAI
from zai import ZhipuAiClient

from backend.settings.config import settings

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=2)
# 支持的供应商：key 为标识，value 为展示名
SUPPORTED_PROVIDERS = {
    "zhipu": "智谱",
    "dashscope": "千问（百炼）",
    "custom": "自定义 OpenAI 兼容",
}
# 各供应商所需的环境变量，用于校验是否已配置密钥
PROVIDER_KEY_ENV = {
    "zhipu": "ZHIPU_API_KEY",
    "dashscope": "DASHSCOPE_API_KEY",
    "custom": "CUSTOM_API_KEY",
}


def provider_available(provider: str) -> bool:
    """判断某供应商是否已配置服务端密钥（密钥仅存在于后端环境变量）。"""
    key = _provider_api_key(provider)
    if provider == "dashscope":
        return bool(key and settings.dashscope_workspace_id)
    if provider == "custom":
        return bool(key and settings.custom_base_url)
    return bool(key)


def provider_default_model(provider: str) -> str:
    """返回供应商的默认模型名（环境变量可覆盖）。"""
    defaults = {
        "zhipu": settings.zhipu_default_model,
        "dashscope": settings.dashscope_default_model,
        "custom": settings.custom_default_model,
    }
    return defaults.get(provider, "").strip()


def _provider_api_key(provider: str) -> str:
    """读取指定供应商的后端环境变量密钥。"""
    keys = {
        "zhipu": settings.zhipu_api_key,
        "dashscope": settings.dashscope_api_key,
        "custom": settings.custom_api_key,
    }
    return (keys.get(provider) or "").strip()


def _resolve_base_url(provider: str) -> str:
    """解析 OpenAI 兼容供应商的 base_url：千问按 workspace_id 拼接，custom 直接取配置。"""
    if provider == "dashscope":
        workspace_id = settings.dashscope_workspace_id.strip()
        if not workspace_id:
            raise ValueError("使用千问提取时必须配置后端环境变量 DASHSCOPE_WORKSPACE_ID")
        return f"https://{workspace_id}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    if provider == "custom":
        base_url = settings.custom_base_url.strip()
        if not base_url:
            raise ValueError("使用自定义供应商时必须配置后端环境变量 CUSTOM_BASE_URL")
        return base_url
    raise ValueError(f"供应商 {provider} 不支持 OpenAI 兼容协议")


async def _call_ai_api(prompt: str, provider: str = "zhipu", model: str = "") -> Dict:
    """按供应商分发调用：智谱走 SDK，其余走 OpenAI 兼容协议。"""
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"不支持的 AI 供应商: {provider}")

    api_key = _provider_api_key(provider)
    if not api_key:
        env_name = PROVIDER_KEY_ENV[provider]
        logger.error("[AI Extractor] 未配置 %s", env_name)
        raise ValueError(f"使用 {SUPPORTED_PROVIDERS[provider]} 提取时必须配置后端环境变量 {env_name}")

    # 模型优先级：显式传入 > 供应商默认
    selected_model = (model or "").strip() or provider_default_model(provider)
    if not selected_model:
        raise ValueError(f"供应商 {SUPPORTED_PROVIDERS[provider]} 未配置默认模型，请先在页面中录入模型")

    try:
        if provider == "zhipu":
            # 智谱 SDK 专路
            client = ZhipuAiClient(api_key=api_key)
            response = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
        else:
            # 千问 / 自定义供应商：OpenAI 兼容协议
            client = OpenAI(api_key=api_key, base_url=_resolve_base_url(provider))
            response = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
        content = response.choices[0].message.content
        if not content:
            raise ValueError(f"{SUPPORTED_PROVIDERS[provider]} API 响应内容为空")
        return {"content": content}
    except ValueError:
        raise
    except Exception as exc:
        logger.error("[AI Extractor] %s API 调用失败: %s", SUPPORTED_PROVIDERS[provider], exc, exc_info=True)
        raise ValueError(f"{SUPPORTED_PROVIDERS[provider]} AI 调用失败: {exc}")


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
    provider: str = "zhipu",
    model: str = "",
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

    result = await _call_ai_api(prompt=prompt, provider=provider, model=model)
    return _parse_json_response(result["content"].strip())


def _extract_article_summary_sync(
    content: str,
    provider: str = "zhipu",
    model: str = "",
) -> Dict:
    """在线程池中同步提取摘要和关键词。"""
    prompt = f"""从以下文章内容提取摘要和关键词：

{_clean_text(content)}

只返回 JSON：{{"summary":"100-200字摘要","keywords":"关键词,关键词,关键词"}}"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_call_ai_api(prompt, provider, model))
        return _parse_json_response(result["content"].strip())
    finally:
        loop.close()


async def extract_article_summary(
    content: str,
    provider: str = "zhipu",
    model: str = "",
) -> Dict:
    """从已有文章内容中提取摘要和关键词。"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _extract_article_summary_sync, content, provider, model)


async def extract_article_async(article_id: int) -> bool:
    """使用后端密钥异步提取文章摘要和关键词，并记录失败状态。"""
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
