from .base import BaseConverter
import aiofiles


class MarkdownConverter(BaseConverter):
    """Markdown 文档转换器"""

    @classmethod
    def supports(cls, filename: str) -> bool:
        """判断是否支持该文件类型"""
        return filename.lower().endswith((".md", ".markdown"))

    @classmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        """
        转换 Markdown 文档
        :return: (markdown_content, title)
        """
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()

        # 提取标题
        title = "未命名文档"
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break
            elif line:
                title = line
                break

        return content, title
