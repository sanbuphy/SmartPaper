"""
此测试文件用于测试各种格式文件到Markdown的转换功能。支持多种输入格式，包括PDF、Word、PPT、Excel、图片、文本文件等，以及通过URL获取的在线文件。转换过程支持OCR文字识别，并可选择性地使用LLM进行图片描述生成。所有转换结果都会保存为markdown格式，并包含元数据、图片信息等完整内容。

示例用法：
    test_file_conversion("docs/example.pdf", use_llm=True)  # 转换本地PDF文件，使用LLM进行图片描述
    test_url_conversion("https://example.com/doc.pdf", use_llm=False)  # 转换在线文件，不使用LLM
"""

import os
import sys
from typing import Dict
from pprint import pprint
from openai import OpenAI

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.markdown_converter import MarkdownConverter


def test_file_conversion(file_path: str, use_llm: bool = False):
    """测试文件转换

    Args:
        file_path (str): 文件路径
        use_llm (bool): 是否使用LLM（用于图片描述等）
    """
    # 配置LLM客户端（如果需要）
    llm_client = None
    llm_model = None
    if use_llm:
        llm_client = OpenAI()
        llm_model = "gpt-4-vision-preview"  # 或其他支持图片的模型

    # 配置转换器
    config = {
        "ocr_enabled": True,  # 启用OCR
    }

    converter = MarkdownConverter(config=config, llm_client=llm_client, llm_model=llm_model)

    print(f"\n{'='*50}")
    print(f"测试文件转换")
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

        # 打印Markdown内容预览
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


def test_url_conversion(url: str, use_llm: bool = False):
    """测试URL文件转换

    Args:
        url (str): 文件URL
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

    converter = MarkdownConverter(config=config, llm_client=llm_client, llm_model=llm_model)

    print(f"\n{'='*50}")
    print(f"测试URL文件转换")
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

        # 打印Markdown内容预览
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
        # 文档
        "pdf": "docs/example.pdf",
        "word": "docs/example.docx",
        "ppt": "docs/example.pptx",
        "excel": "docs/example.xlsx",
        # 图片
        "image": "docs/example.jpg",
        # 文本
        "text": "docs/example.txt",
        "json": "docs/example.json",
        "yaml": "docs/example.yaml",
        "html": "docs/example.html",
        # URL
        "url": "https://arxiv.org/pdf/2312.12456.pdf",
    }

    # 测试本地文件转换（不使用LLM）
    print("\n=== 测试本地文件转换（不使用LLM）===")
    for file_type, file_path in TEST_FILES.items():
        if file_type != "url" and os.path.exists(file_path):
            test_file_conversion(file_path, use_llm=False)

    # 测试本地文件转换（使用LLM）
    print("\n=== 测试本地文件转换（使用LLM）===")
    for file_type, file_path in TEST_FILES.items():
        if file_type in ["image", "pdf"] and os.path.exists(file_path):
            test_file_conversion(file_path, use_llm=True)

    # 测试URL文件转换
    print("\n=== 测试URL文件转换 ===")
    test_url_conversion(TEST_FILES["url"], use_llm=False)
