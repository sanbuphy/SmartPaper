"""
使用 pytest 测试通过URL链接分析学术论文的功能。
支持两种分析模式：提示词模式（prompt）和智能代理模式（agent）。
"""

import os
import pytest
import yaml
from typing import Dict

from src.core.reader import SmartPaper
from src.core.prompt_library import list_prompts


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


def test_url_prompt_default(reader, sample_paper_url):
    """测试URL论文的默认提示词模式"""
    result = reader.process_paper_url(sample_paper_url, mode="prompt")

    assert isinstance(result, dict)
    assert "result" in result
    assert isinstance(result["result"], str)
    assert len(result["result"]) > 0


def test_url_prompt_custom(reader, sample_paper_url):
    """测试URL论文的自定义提示词模式"""
    # 获取第一个可用的提示词
    available_prompts = list_prompts()
    first_prompt = next(iter(available_prompts))

    result = reader.process_paper_url(sample_paper_url, mode="prompt", prompt_name=first_prompt)

    assert isinstance(result, dict)
    assert "result" in result
    assert isinstance(result["result"], str)
    assert len(result["result"]) > 0


def test_url_agent(reader, sample_paper_url):
    """测试URL论文的Agent模式"""
    result = reader.process_paper_url(sample_paper_url, mode="agent")

    assert isinstance(result, dict)
    assert any(key in result for key in ["result", "structured_analysis"])

    if "structured_analysis" in result:
        assert isinstance(result["structured_analysis"], dict)
        assert len(result["structured_analysis"]) > 0
    else:
        assert isinstance(result["result"], str)
        assert len(result["result"]) > 0


def test_invalid_url(reader):
    """测试无效URL的处理"""
    invalid_url = "https://invalid-url.com/paper.pdf"

    with pytest.raises(Exception):
        reader.process_paper_url(invalid_url, mode="prompt")


def test_invalid_mode(reader, sample_paper_url):
    """测试无效模式的处理"""
    with pytest.raises(ValueError):
        reader.process_paper_url(sample_paper_url, mode="invalid_mode")
