"""
使用 pytest 测试从arXiv下载论文并转换为Markdown格式的功能。
包括下载论文、保存到临时目录、转换为Markdown等功能测试。
"""

import os
import sys
import pytest
import tempfile
import requests
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.everything_to_text.pdf_to_md_markitdown import MarkdownConverter


@pytest.fixture
def temp_dir():
    """临时目录 fixture"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def arxiv_paper():
    """arXiv论文信息 fixture"""
    return {
        "url": "https://arxiv.org/pdf/1706.03762",
        "paper_id": "1706.03762",
        "expected_title": "Attention Is All You Need",
    }


@pytest.fixture
def converter():
    """Markdown转换器 fixture"""
    return MarkdownConverter()


def test_arxiv_download_success(temp_dir, arxiv_paper):
    """测试成功下载arXiv论文"""
    pdf_path = os.path.join(temp_dir, f"{arxiv_paper['paper_id']}.pdf")

    response = requests.get(arxiv_paper["url"])
    assert response.status_code == 200

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0


def test_arxiv_convert_to_markdown(temp_dir, arxiv_paper, converter):
    """测试将下载的论文转换为Markdown"""
    # 先下载论文
    pdf_path = os.path.join(temp_dir, f"{arxiv_paper['paper_id']}.pdf")
    response = requests.get(arxiv_paper["url"])
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    # 转换为Markdown
    result = converter.convert(pdf_path)

    assert isinstance(result, dict)
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0

    # 检查是否包含论文标题
    assert arxiv_paper["expected_title"] in result["text_content"]


def test_arxiv_content_processing(temp_dir, arxiv_paper, converter):
    """测试论文内容处理（去除参考文献等）"""
    # 先下载论文
    pdf_path = os.path.join(temp_dir, f"{arxiv_paper['paper_id']}.pdf")
    response = requests.get(arxiv_paper["url"])
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    # 转换并处理内容
    result = converter.convert(pdf_path)["text_content"]

    # 只保留References之前的内容
    if "References" in result:
        result = result.split("References")[0]
    result = "\n".join([line for line in result.split("\n") if line.strip()])

    assert len(result) > 0
    assert "References" not in result
    assert not any(line.isspace() for line in result.split("\n"))


def test_invalid_arxiv_url():
    """测试无效的arXiv URL"""
    invalid_url = "https://arxiv.org/pdf/invalid_id"

    with pytest.raises(Exception):
        response = requests.get(invalid_url)
        response.raise_for_status()


def test_arxiv_metadata(temp_dir, arxiv_paper, converter):
    """测试arXiv论文元数据提取"""
    # 先下载论文
    pdf_path = os.path.join(temp_dir, f"{arxiv_paper['paper_id']}.pdf")
    response = requests.get(arxiv_paper["url"])
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    result = converter.convert(pdf_path)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert isinstance(result["metadata"], dict)

    # 检查元数据字段
    metadata = result["metadata"]
    assert any(key in metadata for key in ["title", "author", "date"])
