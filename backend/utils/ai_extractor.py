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

# 初始化客户端
client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=settings.ark_api_key,
)


def _parse_json_response(result_text: str) -> Dict:
    """解析 AI 返回的 JSON 结果"""
    result_text = result_text.strip()

    # 移除 markdown 代码块标记
    if result_text.startswith("```json"):
        result_text = result_text[7:]
    if result_text.startswith("```"):
        result_text = result_text[3:]
    if result_text.endswith("```"):
        result_text = result_text[:-3]
    result_text = result_text.strip()

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        # 如果解析失败，尝试提取 JSON 部分
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(result_text[start:end])
        raise


async def extract_article_from_url(url: str, html_content: str) -> Dict:
    """
    从网页 URL 和内容中提取文章信息

    Args:
        url: 文章链接
        html_content: 网页内容

    Returns:
        包含 title, content, summary, keywords 的字典
    """
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
        # 直接调用 SDK（同步方式，与 12.py 相同）
        response = client.responses.create(
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
    prompt = f"""从以下文章内容提取摘要和关键词：

{content}

返回JSON格式：
{{"summary":"100-200字摘要","keywords":"关键词1,关键词2,关键词3"}}"""

    # 直接调用 SDK
    response = client.responses.create(
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
