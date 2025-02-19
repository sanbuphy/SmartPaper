import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from src.core.processor import PaperProcessor
from unittest.mock import MagicMock, patch
from langchain.schema import AIMessage, HumanMessage
import yaml


@pytest.fixture
def mock_config():
    return {
        'llm': {
            'provider': 'openai',
            'max_requests': 10,
            'openai': {
                'api_key': 'test-key',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 2000
            }
        },
        'prompts': {
            'default': 'test_prompt'
        }
    }

@pytest.fixture
def processor(mock_config):
    with patch('src.utils.llm_adapter.ChatOpenAI'):
        return PaperProcessor(mock_config)

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_stream_chat():
    """测试真实的流式对话"""
    config = load_config()
    processor = PaperProcessor(config)
    
    # 进行对话测试
    questions = [
        "你是谁？",
        "你能做什么？", 
        "总结一下我们的对话"
    ]
    
    for question in questions:
        print(f"\n用户: {question}")
        print("助手: ", end='', flush=True)
        
        # 使用流式对话
        messages = [HumanMessage(content=question)]
        for chunk in processor._stream_chat(messages):
            print(chunk, end='', flush=True)
        print()  # 换行

if __name__ == '__main__':
    test_stream_chat()