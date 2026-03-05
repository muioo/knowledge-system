from .base import BaseConverter
import aiofiles
import re


class HTMLConverter(BaseConverter):
    """HTML 文档转换器"""

    @classmethod
    def supports(cls, filename: str) -> bool:
        """判断是否支持该文件类型"""
        return filename.lower().endswith((".html", ".htm"))

    @classmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        """
        转换 HTML 文档为 Markdown
        :return: (markdown_content, title)
        """
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            html = await f.read()

        # 提取标题
        title = "未命名文档"
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # 尝试从 h1 标签提取
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
            if h1_match:
                title = h1_match.group(1).strip()

        # 简单的 HTML 到 Markdown 转换
        markdown = html

        # 移除 script 和 style 标签
        markdown = re.sub(r'<script[^>]*>.*?</script>', '', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<style[^>]*>.*?</style>', '', markdown, flags=re.IGNORECASE | re.DOTALL)

        # 转换标题
        markdown = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', markdown, flags=re.IGNORECASE | re.DOTALL)

        # 转换粗体和斜体
        markdown = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', markdown, flags=re.IGNORECASE | re.DOTALL)

        # 转换链接
        markdown = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', markdown, flags=re.IGNORECASE | re.DOTALL)

        # 转换图片
        markdown = re.sub(r'<img[^>]*src="([^"]*)"[^>]*>', r'!\1', markdown, flags=re.IGNORECASE | re.DOTALL)

        # 转换段落和换行
        markdown = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<br\s*/?>', '\n', markdown, flags=re.IGNORECASE)

        # 转换列表
        markdown = re.sub(r'<ul[^>]*>', '', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'</ul>', '', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'<ol[^>]*>', '', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'</ol>', '', markdown, flags=re.IGNORECASE)
        markdown = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', markdown, flags=re.IGNORECASE | re.DOTALL)

        # 转换代码块
        markdown = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', markdown, flags=re.IGNORECASE | re.DOTALL)
        markdown = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```', markdown, flags=re.IGNORECASE | re.DOTALL)

        # 移除剩余的 HTML 标签
        markdown = re.sub(r'<[^>]+>', '', markdown)

        # 清理多余的空行
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        content = markdown.strip()
        return content, title
