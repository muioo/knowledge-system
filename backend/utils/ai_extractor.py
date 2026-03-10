"""AI 提取工具 - 使用火山引擎大模型从网页内容提取文章信息"""
import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional

from volcenginesdkarkruntime import Ark

from backend.settings.config import settings

# 创建线程池用于执行同步的 AI 调用
_executor = ThreadPoolExecutor(max_workers=2)

# 初始化默认客户端（使用配置文件中的 API Key）
_default_client = None


def _get_client(api_key: Optional[str] = None) -> Ark:
    """获取 AI 客户端"""
    global _default_client
    if api_key:
        return Ark(
            base_url='https://ark.cn-beijing.volces.com/api/v3',
            api_key=api_key,
        )
    else:
        if _default_client is None:
            _default_client = Ark(
                base_url='https://ark.cn-beijing.volces.com/api/v3',
                api_key=settings.ark_api_key,
            )
        return _default_client


def _clean_text(text: str) -> str:
    """清理文本中的控制字符"""
    # 保留换行符和制表符，移除其他控制字符
    import re

    # 移除 ASCII 控制字符（除了换行、制表符、回车）
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # 移除 Unicode 控制字符（零宽字符、不可见字符等）
    # \u2000-\u200f: 各种空格和零宽字符
    # \u2028-\u2029: 行分隔符、段落分隔符
    # \u202a-\u202e: 嵌入 directional markers
    # \u2060-\u206f: 其他格式控制字符
    # \ufff9-\ufffb: 插入字符
    # \ufffe-\uffff: 非字符
    text = re.sub(r'[\u2000-\u200f\u2028-\u202e\u2060-\u206f\ufff9-\ufffb\ufffe-\uffff]', '', text)

    # 移除控制字符的其他 Unicode 块
    # \u0000-\u001f: C0 控制字符（已处理，双重保险）
    # \u007f-\u009f: C1 控制字符
    text = re.sub(r'[\u007f-\u009f]', '', text)

    return text


def _clean_json_strings(obj) -> Dict:
    """递归清理 JSON 对象中的所有字符串值"""
    import logging
    logger = logging.getLogger(__name__)

    if isinstance(obj, str):
        # 清理字符串中的控制字符
        cleaned = _clean_text(obj)
        if len(cleaned) != len(obj):
            logger.debug(f"[AI Extractor] 清理字符串: {len(obj)} -> {len(cleaned)} 字符")
        return cleaned
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

    # 记录原始内容长度
    original_length = len(result_text)
    logger.info(f"[AI Extractor] 原始返回内容长度: {original_length} 字符")

    # 先清理控制字符
    result_text = _clean_text(result_text)
    result_text = result_text.strip()

    # 记录清理后长度
    cleaned_length = len(result_text)
    if cleaned_length != original_length:
        logger.info(f"[AI Extractor] 清理控制字符后: {cleaned_length} 字符 (移除 {original_length - cleaned_length} 字符)")

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
        # 递归清理所有字符串值
        parsed = _clean_json_strings(parsed)
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"[AI Extractor] JSON 解析失败: {str(e)}")
        logger.error(f"[AI Extractor] 错误位置: line {e.lineno}, column {e.colno}, pos {e.pos}")

        # 如果解析失败，尝试提取 JSON 部分
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = result_text[start:end]
            # 再次清理
            json_str = _clean_text(json_str)
            try:
                parsed = json.loads(json_str)
                # 递归清理所有字符串值
                parsed = _clean_json_strings(parsed)
                return parsed
            except json.JSONDecodeError as e2:
                logger.error(f"[AI Extractor] 第二次 JSON 解析也失败: {str(e2)}")

        # 输出部分原始内容用于调试（最多500字符）
        debug_content = result_text[:500]
        logger.error(f"[AI Extractor] AI返回内容片段: {debug_content}")

        raise ValueError(f"JSON解析失败: {str(e)}, AI返回内容: {result_text[:200]}")


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
    # 清理 HTML 内容中的控制字符
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
        # 获取客户端（使用传入的 API Key 或默认的）
        ai_client = _get_client(api_key)

        # 直接调用 SDK（同步方式，与 12.py 相同）
        response = ai_client.responses.create(
            model="ep-20260302234602-pz4hc",
            input=[{"role": "user", "content": prompt}],
        )

        # 获取返回内容
        # output[0] 是推理过程，output[1] 是实际输出
        result_text = response.output[1].content[0].text.strip()

        # 解析 JSON
        return _parse_json_response(result_text)

    except Exception as e:
        raise ValueError(f"AI 提取失败: {str(e)}")


def _extract_article_summary_sync(content: str) -> Dict:
    """同步版本的摘要提取（在线程池中运行）"""
    # 清理内容中的控制字符
    content = _clean_text(content)

    prompt = f"""从以下文章内容提取摘要和关键词：

{content}

返回JSON格式：
{{"summary":"100-200字摘要","keywords":"关键词1,关键词2,关键词3"}}"""

    # 获取默认客户端
    ai_client = _get_client()

    # 直接调用 SDK
    response = ai_client.responses.create(
        model="ep-20260302234602-pz4hc",
        input=[{"role": "user", "content": prompt}],
    )

    # 获取返回内容
    result_text = response.output[1].content[0].text.strip()

    # 解析 JSON
    return _parse_json_response(result_text)


async def extract_article_summary(content: str) -> Dict:
    """
    从已有内容中提取摘要和关键词（优化版本，使用线程池避免阻塞）

    Args:
        content: 文章内容

    Returns:
        包含 summary, keywords 的字典
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _extract_article_summary_sync, content)


async def extract_article_async(article_id: int) -> bool:
    """
    异步提取文章摘要和关键词（用于后台任务）
    优化版本：只提取摘要和关键词，减少 token 消耗
    """
    import aiofiles
    from backend.models import Article
    from backend.settings.config import settings

    try:
        # 获取文章
        article = await Article.get(id=article_id)

        # 更新状态为处理中
        article.processing_status = "processing"
        await article.save()

        # 读取本地 HTML 文件
        if not article.html_path:
            print(f"[AI Extractor] Article {article_id}: No html_path")
            return False

        # 使用 settings.upload_dir 作为基础目录
        html_path = os.path.join(settings.upload_dir, article.html_path)

        if not os.path.exists(html_path):
            print(f"[AI Extractor] Article {article_id}: File not found: {html_path}")
            return False

        async with aiofiles.open(html_path, 'r', encoding='utf-8') as f:
            html_content = await f.read()

        print(f"[AI Extractor] Article {article_id}: Read {len(html_content)} chars from HTML")

        # 优化：只截取正文内容（最多 5000 字符），减少 token 消耗
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除 script、style 等标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        # 获取纯文本内容
        text_content = soup.get_text(separator=' ', strip=True)
        text_content = ' '.join(text_content.split())[:5000]  # 最多 5000 字符

        print(f"[AI Extractor] Article {article_id}: Using {len(text_content)} chars for AI")

        # 调用 AI 提取（使用专门的摘要提取函数，更高效）
        result = await extract_article_summary(text_content)

        print(f"[AI Extractor] Article {article_id}: AI result keys: {result.keys()}")

        # 更新文章
        article.summary = result.get("summary")
        article.keywords = result.get("keywords")
        article.processing_status = "completed"
        await article.save()

        print(f"[AI Extractor] Article {article_id}: Successfully extracted")
        return True

    except Exception as e:
        print(f"[AI Extractor] Article {article_id}: Failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

        # 标记为失败
        try:
            article = await Article.get(id=article_id)
            article.processing_status = "failed"
            await article.save()
        except Exception:
            pass
        return False
