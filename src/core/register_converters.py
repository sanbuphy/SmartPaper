"""注册所有文档转换器

这个模块负责注册所有可用的文档转换器。
新的转换器应该在这里注册。
"""

from pathlib import Path
from typing import Dict, Any, Optional
from .document_converter import DocumentConverter

# 导入所有转换器
try:
    from src.tools.everything_to_text.pdf_to_md_mineru import mineru_pdf2md

    _has_mineru = True
except ImportError:
    _has_mineru = False

try:
    from src.tools.everything_to_text.pdf_to_md_markitdown import markitdown_pdf2md

    _has_markitdown = True
except ImportError:
    _has_markitdown = False

try:
    from src.tools.everything_to_text.pdf_to_md_pdfplumber import pdfplumber_pdf2md
    
    _has_pdfplumber = True
except ImportError:
    _has_pdfplumber = False

try:
    from src.tools.everything_to_text.pdf_to_md_fitz import fitz_pdf2md
    
    _has_fitz = True
except ImportError:
    _has_fitz = False


def register_all_converters():
    """注册所有可用的转换器"""
    # 注册 MarkItDown 转换器（作为默认PDF转换器）
    if _has_markitdown:
        DocumentConverter.register("markitdown", markitdown_pdf2md)

    # 注册 Mineru 转换器
    if _has_mineru:
        DocumentConverter.register("mineru", mineru_pdf2md)
        
    # 注册 PDFPlumber 转换器
    if _has_pdfplumber:
        DocumentConverter.register("pdfplumber", pdfplumber_pdf2md)
        
    # 注册 Fitz(PyMuPDF) 转换器
    if _has_fitz:
        DocumentConverter.register("fitz", fitz_pdf2md)

    # 在这里添加更多转换器的注册...


# 在模块导入时自动注册所有转换器
register_all_converters()
