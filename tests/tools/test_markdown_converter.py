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

from src.core.document_converter import convert_to_text


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
def basic_config():
    """基础配置 fixture"""
    return {"ocr_enabled": True}


@pytest.fixture
def llm_client():
    """LLM客户端 fixture"""
    return OpenAI()


@pytest.fixture
def llm_model():
    """LLM模型 fixture"""
    return "gpt-4-vision-preview"


def test_convert_pdf(test_files, basic_config):
    """测试PDF文件转换"""
    if not os.path.exists(test_files["pdf"]):
        pytest.skip("PDF测试文件不存在")

    result = convert_to_text(test_files["pdf"], config=basic_config)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0


def test_convert_image_with_llm(test_files, basic_config, llm_client, llm_model):
    """测试带LLM的图片转换"""
    if not os.path.exists(test_files["image"]):
        pytest.skip("图片测试文件不存在")

    result = convert_to_text(
        test_files["image"], config=basic_config, llm_client=llm_client, llm_model=llm_model
    )

    assert isinstance(result, dict)
    assert "images" in result
    assert len(result["images"]) > 0
    for img in result["images"]:
        assert "path" in img
        assert "description" in img
        assert isinstance(img["description"], str)


def test_convert_invalid_file(basic_config):
    """测试无效文件转换"""
    with pytest.raises(Exception):
        convert_to_text("invalid_file.pdf", config=basic_config)


def test_convert_text_file(test_files, basic_config):
    """测试文本文件转换"""
    if not os.path.exists(test_files["text"]):
        pytest.skip("文本测试文件不存在")

    result = convert_to_text(test_files["text"], config=basic_config)

    assert isinstance(result, dict)
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0


@pytest.mark.parametrize("file_type", ["word", "ppt", "excel"])
def test_convert_office_files(test_files, basic_config, file_type):
    """测试Office文件转换"""
    if not os.path.exists(test_files[file_type]):
        pytest.skip(f"{file_type}测试文件不存在")

    result = convert_to_text(test_files[file_type], config=basic_config)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0
