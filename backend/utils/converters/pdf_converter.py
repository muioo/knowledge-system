from .base import BaseConverter
import pdfplumber


class PDFConverter(BaseConverter):
    """PDF 文档转换器"""

    @classmethod
    def supports(cls, filename: str) -> bool:
        """判断是否支持该文件类型"""
        return filename.lower().endswith(".pdf")

    @classmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        """
        转换 PDF 文档为 Markdown
        :return: (markdown_content, title)
        """
        markdown_lines = []
        title = "未命名文档"

        with pdfplumber.open(file_path) as pdf:
            # 提取第一页的标题
            if pdf.pages:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                if text:
                    lines = text.split("\n")
                    for line in lines:
                        line = line.strip()
                        if line:
                            title = line
                            break

            # 转换所有页面
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    markdown_lines.append(text)

        content = "\n\n".join(markdown_lines)
        return content, title
