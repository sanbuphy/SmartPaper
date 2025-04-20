"""
此测试文件用于测试系统的流式对话功能。它包含了单元测试和集成测试两部分：单元测试使用mock对象测试对话处理器的基本功能，集成测试则通过实际的API调用测试流式对话的效果。测试内容包括配置加载、对话生成、流式响应等核心功能。

示例用法：
    pytest test_stream.py  # 运行单元测试
    python test_stream.py  # 运行集成测试，进行实际的流式对话测试
"""

import os
from loguru import logger


import pytest
from core.llm_wrapper import LLMWrapper
from unittest.mock import MagicMock, patch
from langchain.schema import AIMessage, HumanMessage
import yaml


@pytest.fixture
def mock_config():
    return {
        "llm": {
            "provider": "openai",
            "max_requests": 10,
            "openai": {
                "api_key": "test-key",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000,
            },
        },
        "prompts": {"default": "test_prompt"},
    }


@pytest.fixture
def processor(mock_config):
    with patch("utils.llm_adapter.ChatOpenAI"):
        return LLMWrapper(mock_config)


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_stream_chat():
    """测试真实的流式对话"""
    logger.info("开始测试: 真实的流式对话功能")
    config = load_config()
    processor = LLMWrapper(config)

    # 进行对话测试
    questions = ["你是谁？", "你能做什么？", "总结一下我们的对话"]

    for question in questions:
        logger.info(f"\n用户: {question}")
        logger.info("助手: ", end="", flush=True)

        # 使用流式对话
        messages = [HumanMessage(content=question)]
        for chunk in processor._stream_chat(messages):
            logger.info(chunk, end="", flush=True)
        logger.info()  # 换行


if __name__ == "__main__":
    test_stream_chat()
