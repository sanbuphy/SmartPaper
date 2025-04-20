"""
测试 mineru 转换 PDF 为 Markdown 的功能，
主要判断依据是是否在指定的输出目录下生成了 Markdown 文件。
"""

import os
import sys
import shutil

import pytest

# 将项目根目录添加到 sys.path，以便导入模块


from utils.get_abs_path import get_abs_path
from tools.everything_to_text.pdf_to_md_mineru import mineru_pdf2md


# 测试 mineru_pdf2md 的输出位置功能
def test_mineru_pdf2md_output_location():
    # 测试输入和输出路径
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = "test_datas/test_mineru_add_image_description_如何阅读一本书.pdf"
    output_dir = "test_datas/test_mineru_outputs"
    abs_pdf_path = os.path.join(current_file_dir, pdf_path)
    abs_output_dir = os.path.join(current_file_dir, output_dir)

    # 确保输入的 PDF 文件存在
    assert os.path.exists(abs_pdf_path), f"测试 PDF 文件未找到：{abs_pdf_path}"

    # 清理之前的输出目录（如果存在）
    if os.path.exists(abs_output_dir):
        shutil.rmtree(abs_output_dir)

    try:
        # 执行转换
        result_path = mineru_pdf2md(abs_pdf_path, abs_output_dir)

        # 断言检查
        assert result_path is not None, "转换返回了 None"
        assert os.path.exists(result_path), f"Markdown 文件未找到：{result_path}"
        assert os.path.basename(os.path.dirname(result_path)) == os.path.basename(abs_output_dir), (
            f"Markdown 文件未生成在预期目录。\n"
            f"预期目录：{os.path.basename(abs_output_dir)}\n"
            f"实际目录：{os.path.basename(os.path.dirname(result_path))}"
        )
    except Exception as e:
        pytest.fail(f"转换过程中抛出异常：{e}")
    # finally:
    #     # 清理输出目录
    #     if os.path.exists(abs_output_dir):
    #         shutil.rmtree(abs_output_dir)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
