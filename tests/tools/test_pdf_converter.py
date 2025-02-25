"""
使用 pytest 测试PDF文件转换功能。
支持本地PDF文件和URL链接的PDF文件的转换，包括文本提取、图片提取、OCR识别等功能。
"""

import os
import sys
import pytest
from typing import Dict
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.pdf_converter import PDFConverter


@pytest.fixture
def test_files():
    """测试文件路径 fixture"""
    return {"local_pdf": "papers/example.pdf", "url_pdf": "https://arxiv.org/pdf/2312.12456.pdf"}


@pytest.fixture
def converter():
    """基础PDF转换器 fixture"""
    config = {"ocr_enabled": True}
    return PDFConverter(config=config)


@pytest.fixture
def converter_with_llm():
    """带LLM的PDF转换器 fixture"""
    config = {"ocr_enabled": True}
    llm_client = OpenAI()
    llm_model = "gpt-4-vision-preview"
    return PDFConverter(config=config, llm_client=llm_client, llm_model=llm_model)


def test_local_pdf_basic(converter, test_files):
    """测试基本的本地PDF文件转换"""
    if not os.path.exists(test_files["local_pdf"]):
        pytest.skip("本地PDF测试文件不存在")

    result = converter.convert(test_files["local_pdf"])

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0


def test_local_pdf_with_llm(converter_with_llm, test_files):
    """测试带LLM的本地PDF文件转换"""
    if not os.path.exists(test_files["local_pdf"]):
        pytest.skip("本地PDF测试文件不存在")

    result = converter_with_llm.convert(test_files["local_pdf"])

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert "images" in result

    if result["images"]:
        for img in result["images"]:
            assert "path" in img
            assert "description" in img
            assert isinstance(img["description"], str)


def test_url_pdf_basic(converter, test_files):
    """测试基本的URL PDF文件转换"""
    result = converter.convert_url(test_files["url_pdf"])

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0


def test_url_pdf_with_llm(converter_with_llm, test_files):
    """测试带LLM的URL PDF文件转换"""
    result = converter_with_llm.convert_url(test_files["url_pdf"])

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert "images" in result

    if result["images"]:
        for img in result["images"]:
            assert "path" in img
            assert "description" in img
            assert isinstance(img["description"], str)


def test_invalid_local_pdf(converter):
    """测试无效的本地PDF文件"""
    with pytest.raises(Exception):
        converter.convert("invalid.pdf")


def test_invalid_url_pdf(converter):
    """测试无效的URL PDF文件"""
    with pytest.raises(Exception):
        converter.convert_url("https://invalid-url.com/paper.pdf")


def test_pdf_metadata(converter, test_files):
    """测试PDF元数据提取"""
    if not os.path.exists(test_files["local_pdf"]):
        pytest.skip("本地PDF测试文件不存在")

    result = converter.convert(test_files["local_pdf"])

    assert isinstance(result, dict)
    assert "metadata" in result
    assert isinstance(result["metadata"], dict)

    # 检查常见的元数据字段
    expected_fields = ["title", "author", "creation_date", "modification_date"]
    assert any(field in result["metadata"] for field in expected_fields)


@pytest.mark.parametrize("ocr_enabled", [True, False])
def test_pdf_ocr_options(test_files, ocr_enabled):
    """测试不同OCR选项的PDF转换"""
    if not os.path.exists(test_files["local_pdf"]):
        pytest.skip("本地PDF测试文件不存在")

    config = {"ocr_enabled": ocr_enabled}
    converter = PDFConverter(config=config)

    result = converter.convert(test_files["local_pdf"])

    assert isinstance(result, dict)
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0
