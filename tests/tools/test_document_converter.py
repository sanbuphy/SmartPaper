"""
使用 pytest 测试文档转换功能。
支持多种输入格式，包括本地和URL文件的转换，文本提取、图片提取、OCR识别等功能。
"""

import os
import sys
import pytest
from typing import Dict
from openai import OpenAI


from core.document_converter import convert_to_text, convert_url_to_text


@pytest.fixture
def test_files():
    """测试文件路径 fixture"""
    return {
        # 本地PDF文件
        "pdf": "tests/tools/test_datas/test_mineru_add_image_description_如何阅读一本书.pdf",
        # URL文件
        "url_pdf": "https://arxiv.org/pdf/2312.12456.pdf",
    }


@pytest.fixture
def config_basic():
    """基础转换配置 fixture"""
    return {"ocr_enabled": True}


@pytest.fixture
def config_with_llm():
    """带LLM的转换配置 fixture"""
    return {"ocr_enabled": True, "llm_client": OpenAI(), "llm_model": "gpt-4-vision-preview"}


# ---- 基本文档转换测试 ----


def test_convert_pdf(test_files, config_basic):
    """测试PDF文件转换"""
    if not os.path.exists(test_files["pdf"]):
        pytest.skip("PDF测试文件不存在")

    result = convert_to_text(test_files["pdf"], config=config_basic)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0


def test_pdf_to_md_markitdown(test_files, config_basic):
    """特别测试markitdown转换器将PDF转换为Markdown格式"""
    if not os.path.exists(test_files["pdf"]):
        pytest.skip("PDF测试文件不存在")

    # 明确指定使用markitdown转换器
    config = config_basic.copy()

    result = convert_to_text(test_files["pdf"], converter_name="markitdown", config=config)

    assert isinstance(result, dict)
    assert "text_content" in result
    text_content = result["text_content"]

    # 验证文本内容是Markdown格式
    assert isinstance(text_content, str)
    assert len(text_content) > 0

    # 检查是否包含Markdown格式的内容（至少有一些标题、列表等)
    md_elements = [
        "#",  # 标题
        "-",  # 列表
        "*",  # 强调或列表
        "```",  # 代码块
        ">",  # 引用
        "![",  # 图片
        "[",  # 链接
    ]

    has_md_format = any(element in text_content for element in md_elements)
    assert has_md_format, "转换的内容不包含Markdown格式"


@pytest.mark.skip("没有可用的图片测试文件")
def test_convert_image_with_llm(test_files, config_with_llm):
    """测试带LLM的图片转换"""
    pass


def test_convert_invalid_file(config_basic):
    """测试无效文件转换"""
    with pytest.raises(Exception):
        convert_to_text("invalid_file.pdf", config=config_basic)


@pytest.mark.skip("没有可用的文本测试文件")
def test_convert_text_file(test_files, config_basic):
    """测试文本文件转换"""
    pass


@pytest.mark.skip("没有可用的Office测试文件")
@pytest.mark.parametrize("file_type", ["word", "ppt", "excel"])
def test_convert_office_files(test_files, config_basic, file_type):
    """测试Office文件转换"""
    pass


# ---- PDF特定测试 ----


def test_pdf_with_llm(config_with_llm, test_files):
    """测试带LLM的PDF文件转换"""
    if not os.path.exists(test_files["pdf"]):
        pytest.skip("PDF测试文件不存在")

    llm_client = config_with_llm.pop("llm_client")
    llm_model = config_with_llm.pop("llm_model")

    result = convert_to_text(
        test_files["pdf"], config=config_with_llm, llm_client=llm_client, llm_model=llm_model
    )

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert "images" in result

    if result["images"]:
        for img in result["images"]:
            assert "path" in img
            assert "description" in img
            assert isinstance(img["description"], str)


def test_url_pdf_basic(config_basic, test_files):
    """测试基本的URL PDF文件转换"""
    result = convert_url_to_text(test_files["url_pdf"], config=config_basic)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0


def test_url_pdf_with_llm(config_with_llm, test_files):
    """测试带LLM的URL PDF文件转换"""
    llm_client = config_with_llm.pop("llm_client")
    llm_model = config_with_llm.pop("llm_model")

    result = convert_url_to_text(
        test_files["url_pdf"], config=config_with_llm, llm_client=llm_client, llm_model=llm_model
    )

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "text_content" in result
    assert "images" in result

    if result["images"]:
        for img in result["images"]:
            assert "path" in img
            assert "description" in img
            assert isinstance(img["description"], str)


def test_invalid_url_pdf(config_basic):
    """测试无效的URL PDF文件"""
    with pytest.raises(Exception):
        convert_url_to_text("https://invalid-url.com/paper.pdf", config=config_basic)


def test_pdf_metadata(config_basic, test_files):
    """测试PDF元数据提取"""
    if not os.path.exists(test_files["pdf"]):
        pytest.skip("PDF测试文件不存在")

    result = convert_to_text(test_files["pdf"], config=config_basic)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert isinstance(result["metadata"], dict)

    # 检查常见的元数据字段
    expected_fields = ["title", "author", "creation_date", "modification_date"]
    assert any(field in result["metadata"] for field in expected_fields)


@pytest.mark.parametrize("ocr_enabled", [True, False])
def test_pdf_ocr_options(test_files, ocr_enabled):
    """测试不同OCR选项的PDF转换"""
    if not os.path.exists(test_files["pdf"]):
        pytest.skip("PDF测试文件不存在")

    config = {"ocr_enabled": ocr_enabled}

    result = convert_to_text(test_files["pdf"], config=config)

    assert isinstance(result, dict)
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0
