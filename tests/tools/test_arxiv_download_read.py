"""
使用 pytest 测试从arXiv下载论文并转换为Markdown格式的功能。
包括下载论文、保存到临时目录、转换为Markdown等功能测试。
"""

import os
import pytest
import requests
import warnings
from loguru import logger

warnings.simplefilter("error", ResourceWarning)  # 将
from core.document_converter import convert_to_text


@pytest.fixture
def temp_dir():
    """临时目录 fixture"""
    os.makedirs("temp", exist_ok=True)
    temp_dir = "temp"
    yield temp_dir
    # 测试后不删除目录，因为可能需要查看文件


@pytest.fixture
def arxiv_paper():
    """arXiv论文信息 fixture"""
    return {
        "url": "https://arxiv.org/pdf/1706.03762",
        "paper_id": "1706.03762",
        "expected_title": "Attention Is All You Need",
    }


@pytest.fixture
def config():
    """测试配置 fixture"""
    return {"llm": {"max_requests": 3}}


def test_arxiv_download_success(temp_dir, arxiv_paper):
    """测试成功下载arXiv论文"""
    logger.info("====== 开始测试: arXiv论文下载功能 ======")
    pdf_path = os.path.join(temp_dir, f"{arxiv_paper['paper_id']}.pdf")
    logger.info(f"下载论文: {arxiv_paper['url']} 到 {pdf_path}")
    response = requests.get(arxiv_paper["url"])
    assert response.status_code == 200

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0
    logger.info(f"论文下载成功，文件大小: {os.path.getsize(pdf_path)} 字节")
    logger.info("====== arXiv论文下载测试完成 ======")


def test_arxiv_convert_to_markdown(temp_dir, arxiv_paper, config):
    """测试将下载的论文转换为Markdown"""
    logger.info("====== 开始测试: arXiv论文转换为Markdown功能 ======")
    # 先下载论文
    pdf_path = os.path.join(temp_dir, f"{arxiv_paper['paper_id']}.pdf")
    logger.info(f"准备处理论文: {pdf_path}")
    response = requests.get(arxiv_paper["url"])
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    # 转换为Markdown
    logger.info("开始将PDF转换为Markdown...")
    result = convert_to_text(pdf_path, config=config)

    assert isinstance(result, dict)
    assert "text_content" in result
    assert isinstance(result["text_content"], str)
    assert len(result["text_content"]) > 0
    logger.info(f"转换成功，生成的文本长度: {len(result['text_content'])} 字符")

    # 检查是否包含论文标题
    assert arxiv_paper["expected_title"] in result["text_content"]
    logger.info(f"已验证转换后的内容包含论文标题: {arxiv_paper['expected_title']}")
    logger.info("====== arXiv论文转换为Markdown测试完成 ======")


def test_arxiv_content_processing(temp_dir, arxiv_paper, config):
    """测试论文内容处理（去除参考文献等）"""
    logger.info("====== 开始测试: arXiv论文内容处理功能 ======")
    # 先下载论文
    pdf_path = os.path.join(temp_dir, f"{arxiv_paper['paper_id']}.pdf")
    logger.info(f"准备处理论文: {pdf_path}")
    response = requests.get(arxiv_paper["url"])
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    # 转换并处理内容
    logger.info("将PDF转换为文本并进行内容处理...")
    result = convert_to_text(pdf_path, config=config)["text_content"]

    # 只保留References之前的内容
    logger.info("处理论文内容，移除参考文献部分...")
    if "References" in result:
        result = result.split("References")[0]
    result = "\n".join([line for line in result.split("\n") if line.strip()])

    assert len(result) > 0
    assert "References" not in result
    assert not any(line.isspace() for line in result.split("\n"))
    logger.info("内容处理成功，已去除参考文献和空行")
    logger.info("====== arXiv论文内容处理测试完成 ======")


def test_invalid_arxiv_url():
    """测试无效的arXiv URL"""
    logger.info("====== 开始测试: 无效arXiv URL处理 ======")
    invalid_url = "https://arxiv.org/pdf/invalid_id"
    logger.info(f"测试无效URL: {invalid_url}")

    with pytest.raises(Exception):
        response = requests.get(invalid_url)
        response.raise_for_status()

    logger.info("已正确处理无效URL异常")
    logger.info("====== 无效arXiv URL处理测试完成 ======")


def test_arxiv_metadata(temp_dir, arxiv_paper, config):
    """测试arXiv论文元数据提取"""
    logger.info("====== 开始测试: arXiv论文元数据提取功能 ======")
    # 先下载论文
    pdf_path = os.path.join(temp_dir, f"{arxiv_paper['paper_id']}.pdf")
    logger.info(f"准备提取论文元数据: {pdf_path}")
    response = requests.get(arxiv_paper["url"])
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    logger.info("提取论文元数据...")
    result = convert_to_text(pdf_path, config=config)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert isinstance(result["metadata"], dict)

    # 检查元数据字段
    metadata = result["metadata"]
    assert any(key in metadata for key in ["title", "author", "date"])
    logger.info(f"成功提取元数据字段: {', '.join(metadata.keys())}")
    logger.info("====== arXiv论文元数据提取测试完成 ======")
