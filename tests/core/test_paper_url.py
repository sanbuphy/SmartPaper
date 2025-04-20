"""
使用 pytest 测试通过URL链接分析学术论文的功能。
"""

import pytest
import yaml
from loguru import logger

from core.smart_paper_core import SmartPaper
from core.prompt_manager import list_prompts


@pytest.fixture
def config():
    """配置文件 fixture"""
    config_path = "config/config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def reader():
    """SmartPaper reader fixture"""
    return SmartPaper(output_format="markdown")


@pytest.fixture
def sample_paper_url():
    """示例论文URL fixture"""
    return "https://arxiv.org/pdf/2312.12456.pdf"


def test_url_default(reader, sample_paper_url):
    """测试URL论文分析（默认提示词）"""
    logger.info("开始测试: URL论文分析（默认提示词）")
    result = reader.process_paper_url(sample_paper_url)

    assert isinstance(result, dict)
    assert "result" in result
    assert isinstance(result["result"], str)
    assert len(result["result"]) > 0


def test_url_custom_prompt(reader, sample_paper_url):
    """测试URL论文分析（自定义提示词）"""
    logger.info("开始测试: URL论文分析（自定义提示词）")
    # 获取第一个可用的提示词
    available_prompts = list_prompts()
    first_prompt = next(iter(available_prompts))

    result = reader.process_paper_url(sample_paper_url, prompt_name=first_prompt)

    assert isinstance(result, dict)
    assert "result" in result
    assert isinstance(result["result"], str)
    assert len(result["result"]) > 0


def test_invalid_url(reader):
    """测试无效URL的处理"""
    logger.info("开始测试: 无效URL的处理")
    invalid_url = "https://invalid-url.com/paper.pdf"

    with pytest.raises(Exception):
        reader.process_paper_url(invalid_url)
