from .word_converter import WordConverter
from .pdf_converter import PDFConverter
from .ppt_converter import PPTConverter
from .md_converter import MarkdownConverter
from .html_converter import HTMLConverter
from typing import List

CONVERTERS: List[type] = [
    WordConverter,
    PDFConverter,
    PPTConverter,
    MarkdownConverter,
    HTMLConverter,
]


def get_converter(filename: str):
    """根据文件名获取合适的转换器"""
    for converter_class in CONVERTERS:
        if converter_class.supports(filename):
            return converter_class()
    raise ValueError(f"不支持的文件类型: {filename}")


async def convert_document(file_path: str, filename: str) -> tuple[str, str]:
    """
    转换文档为 Markdown 格式
    :param file_path: 文件路径
    :param filename: 文件名
    :return: (markdown_content, title)
    """
    converter = get_converter(filename)
    return await converter.convert(file_path)


__all__ = ["convert_document", "get_converter"]
