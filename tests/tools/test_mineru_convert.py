import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.mineru_convert import process_pdf
from src.utils.get_abs_path import get_abs_path


def test_process_pdf():
    abs_pdf_file = get_abs_path("test_datas/如何阅读一本书-output.pdf")
    abs_output_dir = get_abs_path("test_datas/outputs")
    md_file_path = process_pdf(abs_pdf_file, abs_output_dir)

    assert md_file_path.startswith(
        abs_output_dir
    ), f"生成的 Markdown 文件路径不在指定的输出目录下: {md_file_path}"
