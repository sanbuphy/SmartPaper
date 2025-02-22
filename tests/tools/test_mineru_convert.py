"""
测试mineru 转换 PDF 为 Markdown的功能，
主要判断依据是是否在指定的输出目录下生成了 Markdown 文件。
"""

import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.get_abs_path import get_abs_path
from src.tools.mineru_convert import mineru_pdf2md


# 测试 mineru_pdf2md 的输出位置功能
def test_mineru_pdf2md_output_location():
    # 测试输入和输出路径
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = "test_datas/test_mineru_add_image_description_如何阅读一本书.pdf"
    output_dir = "test_mineru_outputs"
    abs_pdf_path = os.path.join(current_file_dir, pdf_path)
    abs_output_dir = os.path.join(current_file_dir, output_dir)

    # 确保输入的 PDF 文件存在
    assert os.path.exists(abs_pdf_path), f"测试 PDF 文件未找到：{abs_pdf_path}"

    # 执行转换
    result_path = mineru_pdf2md(abs_pdf_path, abs_output_dir)

    # 断言检查
    assert result_path is not None, "转换返回了 None"
    assert os.path.exists(result_path), f"Markdown 文件未找到：{result_path}"
    result1 = os.path.basename(os.path.dirname(result_path))
    result2 = os.path.basename(abs_output_dir)
    assert result1 == result2, (
        f"Markdown 文件未生成在预期目录。\n" f"预期目录：{result1}\n" f"实际目录：{result2}"
    )
