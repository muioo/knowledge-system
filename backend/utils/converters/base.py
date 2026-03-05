from abc import ABC, abstractmethod


class BaseConverter(ABC):
    """文档转换器基类"""

    @classmethod
    @abstractmethod
    def supports(cls, filename: str) -> bool:
        """判断是否支持该文件类型"""
        pass

    @classmethod
    @abstractmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        """
        转换文档为 Markdown 格式
        :return: (markdown_content, title)
        """
        pass
