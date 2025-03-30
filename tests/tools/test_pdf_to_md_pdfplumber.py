"""
测试pdf_to_md_fitz.py文件，用于测试pdf_extractor.py中的process_pdf函数
"""

import os
import pytest

from src.tools.everything_to_text.pdf_to_md_pdfplumber import process_pdf


def test_pdf_to_md_conversion():
    # 定义测试文件和输出路径
    test_pdf_path = "./test_datas/test_pdf_to_md_fitz.pdf"
    output_dir = "./output"
    
    # 获取输入文件名（不含扩展名）
    input_filename = os.path.splitext(os.path.basename(test_pdf_path))[0]
    expected_output_file = os.path.join(output_dir, f"{input_filename}.md")
    
    # 如果输出文件已存在，先删除它以确保测试的准确性
    if os.path.exists(expected_output_file):
        os.remove(expected_output_file)
    
    # 处理PDF文件
    process_pdf(test_pdf_path, output_dir)
    
    # 验证输出文件是否存在
    assert os.path.exists(expected_output_file), f"输出文件 {expected_output_file} 不存在"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
