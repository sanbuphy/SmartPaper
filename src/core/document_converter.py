"""统一的文档转换接口

这个模块提供了一个统一的接口来处理各种文档格式到文本的转换。
通过注册机制，可以灵活地添加新的转换器。
"""

from typing import Callable, Dict, Any, Optional, Union
from pathlib import Path


class DocumentConverter:
    _converters: Dict[str, Callable] = {}

    @classmethod
    def register(cls, file_type: str, converter_func: Callable):
        """注册一个新的转换器

        Args:
            file_type: 文件类型（扩展名，如 'pdf', 'docx' 等）
            converter_func: 转换函数，接收文件路径，返回文本内容
        """
        cls._converters[file_type.lower()] = converter_func

    @classmethod
    def convert_to_text(cls, file_path: Union[str, Path], **kwargs) -> str:
        """将文档转换为文本

        Args:
            file_path: 文件路径
            **kwargs: 传递给具体转换器的额外参数

        Returns:
            str: 转换后的文本内容

        Raises:
            ValueError: 如果文件类型不支持或文件不存在
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        file_type = file_path.suffix.lower().lstrip(".")
        converter = cls._converters.get(file_type)

        if not converter:
            raise ValueError(f"No converter registered for file type: {file_type}")

        return converter(file_path, **kwargs)


# 创建一个便捷的函数接口
def convert_to_text(file_path: Union[str, Path], **kwargs) -> str:
    """便捷的文档转换函数

    Args:
        file_path: 文件路径
        **kwargs: 额外的转换参数

    Returns:
        str: 转换后的文本内容
    """
    return DocumentConverter.convert_to_text(file_path, **kwargs)
