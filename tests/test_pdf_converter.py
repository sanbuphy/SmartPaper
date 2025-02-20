"""
此测试文件用于测试PDF文件转换功能，支持本地PDF文件和URL链接的PDF文件的转换。它提供了完整的PDF处理功能，包括文本提取、图片提取、OCR识别，以及可选的使用LLM进行图片描述生成。转换结果会以markdown格式保存，并包含元数据、图片信息等完整内容。

示例用法：
    test_local_file("path/to/local.pdf", use_llm=True)  # 转换本地PDF文件，使用LLM进行图片描述
    test_url_file("https://example.com/paper.pdf", use_llm=False)  # 转换在线PDF文件，不使用LLM
"""

import os
import sys
from typing import Dict
from pprint import pprint
from openai import OpenAI

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.pdf_converter import PDFConverter


def test_local_file(file_path: str, use_llm: bool = False):
    """测试本地PDF文件转换

    Args:
        file_path (str): PDF文件路径
        use_llm (bool): 是否使用LLM（用于图片描述等）
    """
    # 配置LLM客户端（如果需要）
    llm_client = None
    llm_model = None
    if use_llm:
        llm_client = OpenAI()
        llm_model = "gpt-4-vision-preview"

    # 配置转换器
    config = {
        "ocr_enabled": True,  # 启用OCR
    }

    converter = PDFConverter(config=config, llm_client=llm_client, llm_model=llm_model)

    print(f"\n{'='*50}")
    print(f"测试PDF文件转换")
    print(f"文件路径: {file_path}")
    print(f"使用LLM: {use_llm}")
    print(f"{'='*50}\n")

    try:
        result = converter.convert(file_path)

        # 打印元数据
        print("文件元数据:")
        print("-" * 30)
        for key, value in result["metadata"].items():
            if value:
                print(f"{key}: {value}")

        # 打印图片信息
        if result["images"]:
            print("\n提取的图片:")
            print("-" * 30)
            for img in result["images"]:
                print(f"路径: {img['path']}")
                if "description" in img and img["description"]:
                    print(f"描述: {img['description']}")

        # 打印文本预览
        print("\nMarkdown内容预览:")
        print("-" * 30)
        preview_text = (
            result["text_content"][:1000] + "..."
            if len(result["text_content"]) > 1000
            else result["text_content"]
        )
        print(preview_text)

        # 保存转换结果
        output_path = f"{os.path.splitext(file_path)[0]}_converted.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text_content"])
        print(f"\n转换结果已保存到: {output_path}")

    except Exception as e:
        print(f"转换失败: {str(e)}")


def test_url_file(url: str, use_llm: bool = False):
    """测试URL PDF文件转换

    Args:
        url (str): PDF文件URL
        use_llm (bool): 是否使用LLM
    """
    # 配置LLM客户端（如果需要）
    llm_client = None
    llm_model = None
    if use_llm:
        llm_client = OpenAI()
        llm_model = "gpt-4-vision-preview"

    # 配置转换器
    config = {
        "ocr_enabled": True,
    }

    converter = PDFConverter(config=config, llm_client=llm_client, llm_model=llm_model)

    print(f"\n{'='*50}")
    print(f"测试URL PDF文件转换")
    print(f"文件URL: {url}")
    print(f"使用LLM: {use_llm}")
    print(f"{'='*50}\n")

    try:
        result = converter.convert_url(url)

        # 打印元数据
        print("文件元数据:")
        print("-" * 30)
        for key, value in result["metadata"].items():
            if value:
                print(f"{key}: {value}")

        # 打印图片信息
        if result["images"]:
            print("\n提取的图片:")
            print("-" * 30)
            for img in result["images"]:
                print(f"路径: {img['path']}")
                if "description" in img and img["description"]:
                    print(f"描述: {img['description']}")

        # 打印文本预览
        print("\nMarkdown内容预览:")
        print("-" * 30)
        preview_text = (
            result["text_content"][:1000] + "..."
            if len(result["text_content"]) > 1000
            else result["text_content"]
        )
        print(preview_text)

        # 保存转换结果
        output_path = "url_converted.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text_content"])
        print(f"\n转换结果已保存到: {output_path}")

    except Exception as e:
        print(f"转换失败: {str(e)}")


if __name__ == "__main__":
    # 测试配置
    TEST_FILES = {
        "local_pdf": "papers/example.pdf",  # 替换为实际的PDF文件路径
        "url_pdf": "https://arxiv.org/pdf/2312.12456.pdf",  # 替换为实际的PDF URL
    }

    # 测试本地PDF文件转换（不使用LLM）
    print("\n=== 测试本地PDF文件转换（不使用LLM）===")
    if os.path.exists(TEST_FILES["local_pdf"]):
        test_local_file(TEST_FILES["local_pdf"], use_llm=False)

    # 测试本地PDF文件转换（使用LLM）
    print("\n=== 测试本地PDF文件转换（使用LLM）===")
    if os.path.exists(TEST_FILES["local_pdf"]):
        test_local_file(TEST_FILES["local_pdf"], use_llm=True)

    # 测试URL PDF文件转换
    print("\n=== 测试URL PDF文件转换 ===")
    test_url_file(TEST_FILES["url_pdf"], use_llm=False)
