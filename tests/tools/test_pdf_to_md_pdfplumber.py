"""
测试pdf_to_md_pdfplumber.py文件，用于测试process_pdf函数
"""

import os
import pytest
import json

from src.tools.everything_to_text.pdf_to_md_pdfplumber import process_pdf


def test_pdf_to_md_conversion():
    # 定义测试文件和输出路径
    test_pdf_path = "test_datas/test_pdf_to_md_pdfplumber.pdf"
    output_dir = "./output"
    
    # 获取输入文件名（不含扩展名）
    input_filename = os.path.splitext(os.path.basename(test_pdf_path))[0]
    expected_md_file = os.path.join(output_dir, f"{input_filename}.md")
    expected_images_json = os.path.join(output_dir, f"{input_filename}_images.json")
    
    # 如果输出文件已存在，先删除它以确保测试的准确性
    if os.path.exists(expected_md_file):
        os.remove(expected_md_file)
    if os.path.exists(expected_images_json):
        os.remove(expected_images_json)
    
    # 处理PDF文件
    result = process_pdf(test_pdf_path, output_dir)
    
    # 验证返回值格式
    assert isinstance(result, tuple), "返回值应为元组"
    assert len(result) == 3, "返回值元组应包含三个元素"
    
    # 验证返回的文本内容是否是字典格式
    text_content = result[0]
    assert isinstance(text_content, dict), "文本内容应为字典格式"
    assert "text_content" in text_content, "文本内容字典中应包含'text_content'键"
    assert "metadata" in text_content, "文本内容字典中应包含'metadata'键"
    assert "images" in text_content, "文本内容字典中应包含'images'键"
    
    # 验证图片列表
    image_paths = result[1]
    assert isinstance(image_paths, list), "图片路径应为列表"
    
    # 验证Markdown文件路径
    md_path = result[2]
    assert os.path.exists(md_path), f"Markdown文件 {md_path} 应存在"
    
    # 验证images.json文件是否存在
    assert os.path.exists(expected_images_json), f"图片JSON文件 {expected_images_json} 应存在"
    
    # 验证JSON文件内容
    with open(expected_images_json, 'r', encoding='utf-8') as f:
        images_data = json.load(f)
        assert isinstance(images_data, dict), "图片JSON应为字典格式"
    
    # 验证图片目录是否存在
    images_dir = os.path.join(output_dir, "images")
    assert os.path.isdir(images_dir), f"图片目录 {images_dir} 应存在"
    
    # 检查是否至少有一些图片被提取
    image_files = [f for f in os.listdir(images_dir) if f.endswith('.png')]
    assert len(image_files) > 0, "应至少提取一些图片"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
