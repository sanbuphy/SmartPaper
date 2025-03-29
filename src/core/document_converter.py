"""统一的文档转换接口

这个模块提供了一个统一的接口来处理各种文档格式到文本的转换。
通过注册机制，可以灵活地添加新的转换器。
"""

from typing import Callable, Dict, Any, Optional, Union
from pathlib import Path


class DocumentConverter:
    _converters: Dict[str, Callable] = {}
    _registered_types: Dict[str, Dict[str, Callable]] = {}

    @classmethod
    def register(cls, converter_name: str, converter_func: Callable):
        """注册一个新的转换器

        Args:
            converter_name: 转换器名称，如 'markitdown', 'mineru' 等
            converter_func: 转换函数，接收文件路径，返回文本内容
        """
        cls._converters[converter_name.lower()] = converter_func

    @classmethod
    def convert_to_text(
        cls, file_path: Union[str, Path], converter_name: str = "markitdown", **kwargs
    ) -> Dict:
        """将文档转换为文本

        Args:
            file_path: 文件路径
            converter_name: 转换器名称，例如 'markitdown', 'mineru' 等，默认使用 'markitdown'
            **kwargs: 传递给具体转换器的额外参数

        Returns:
            Dict: 转换后的结果，包含文本内容和元数据

        Raises:
            ValueError: 如果文件类型不支持或文件不存在，或指定的转换器不存在
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise ValueError(f"文件不存在: {file_path}")

        converter = cls._converters.get(converter_name.lower())
        if not converter:
            # 如果指定的转换器不存在，尝试使用默认的markitdown
            converter = cls._converters.get("markitdown")
            if not converter:
                raise ValueError(
                    f"未找到转换器: {converter_name}，且默认转换器'markitdown'也不可用"
                )

        return converter(file_path, **kwargs)


# 创建一个便捷的函数接口
def convert_to_text(file_path: Union[str, Path], **kwargs) -> Dict:
    """便捷的文档转换函数

    Args:
        file_path: 文件路径
        **kwargs: 额外的转换参数，包括：
                  - config: 配置信息，可以包含 'converter_name' 来指定转换器
                  - converter_name: 直接指定转换器名称，优先级高于config中的设置
                  - llm_client: LLM客户端
                  - llm_model: LLM模型名称

    Returns:
        Dict: 转换后的结果，包含文本内容和元数据
    """
    # 获取配置
    config = kwargs.pop("config", {}) or {}

    # 确定转换器名称：优先使用直接传入的converter_name，其次使用config中的设置，最后默认为"markitdown"
    converter_name = kwargs.pop("converter_name", config.get("converter_name", "markitdown"))

    # 调用转换
    return DocumentConverter.convert_to_text(file_path, converter_name=converter_name, **kwargs)
