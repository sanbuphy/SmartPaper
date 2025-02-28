"""
使用 pytest 测试各种格式文件到Markdown的转换功能。
支持多种输入格式，包括PDF、Word、PPT、Excel、图片、文本文件等。
"""

import os
import sys
import pytest
from typing import Dict
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.everything_to_text.pdf_to_md_markitdown import MarkdownConverter


@pytest.fixture
def test_files():
    """测试文件路径 fixture"""
    return {
        "pdf": "docs/example.pdf",
        "word": "docs/example.docx",
        "ppt": "docs/example.pptx",
        "excel": "docs/example.xlsx",
        "image": "docs/example.jpg",
        "text": "docs/example.txt",
        "json": "docs/example.json",
        "yaml": "docs/example.yaml",
        "html": "docs/example.html",
    }


@pytest.fixture
def sample_url():
    """示例URL fixture"""
    return "https://arxiv.org/pdf/2312.12456.pdf"


@pytest.fixture
def converter():
    """基础转换器 fixture"""
    config = {"ocr_enabled": True}
    return MarkdownConverter(config=config)


@pytest.fixture
def converter_with_llm():
    """带LLM的转换器 fixture"""
    config = {"ocr_enabled": True}
    llm_client = OpenAI()
    llm_model = "gpt-4-vision-preview"
    return MarkdownConverter(config=config, llm_client=llm_client, llm_model=llm_model)


def test_convert_pdf(converter, test_files):
    """测试PDF文件转换"""
    if not os.path.exists(test_files["pdf"]):
        pytest.skip("PDF测试文件不存在")

    result = converter.convert(test_files["pdf"])

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0


def test_convert_image_with_llm(converter_with_llm, test_files):
    """测试带LLM的图片转换"""
    if not os.path.exists(test_files["image"]):
        pytest.skip("图片测试文件不存在")

    result = converter_with_llm.convert(test_files["image"])

    assert isinstance(result, dict)
    assert "images" in result
    assert len(result["images"]) > 0
    for img in result["images"]:
        assert "path" in img
        assert "description" in img
        assert isinstance(img["description"], str)


def test_convert_url(converter, sample_url):
    """测试URL文件转换"""
    result = converter.convert_url(sample_url)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0


def test_convert_invalid_file(converter):
    """测试无效文件转换"""
    with pytest.raises(Exception):
        converter.convert("invalid_file.pdf")


def test_convert_invalid_url(converter):
    """测试无效URL转换"""
    with pytest.raises(Exception):
        converter.convert_url("https://invalid-url.com/doc.pdf")


def test_convert_text_file(converter, test_files):
    """测试文本文件转换"""
    if not os.path.exists(test_files["text"]):
        pytest.skip("文本测试文件不存在")

    result = converter.convert(test_files["text"])

    assert isinstance(result, dict)
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0


@pytest.mark.parametrize("file_type", ["word", "ppt", "excel"])
def test_convert_office_files(converter, test_files, file_type):
    """测试Office文件转换"""
    if not os.path.exists(test_files[file_type]):
        pytest.skip(f"{file_type}测试文件不存在")

    result = converter.convert(test_files[file_type])

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0
