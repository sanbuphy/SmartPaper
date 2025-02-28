"""SmartPaper 核心功能模块"""

from .document_converter import convert_to_text
from . import register_converters

__all__ = ["convert_to_text"]
