"""
测试 ModelManager 类的功能
"""

import os
import sys
import time
import pytest
from typing import Dict, List, Optional


# 添加项目根目录到sys.path，确保可以导入SmartPaper模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from SmartPaper.core.model_manager import ModelManager, chat, chat_with_history
from SmartPaper.core.model_manager import list_available_providers, list_available_models


@pytest.fixture
def manager():
    """创建一个 ModelManager 实例作为测试 fixture"""
    # 使用当前目录的配置文件
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    manager_instance = ModelManager(config_path)
    print(f"初始化 ModelManager 成功，使用配置文件: {manager_instance.config_path}")
    return manager_instance


def test_model_manager_initialization():
    """测试 ModelManager 初始化"""
    # 使用当前目录的配置文件
    config_path = "config.yaml"
    manager = ModelManager(config_path)
    print(f"初始化 ModelManager 成功，使用配置文件: {manager.config_path}")
    return manager


def test_list_providers_and_models(manager: ModelManager):
    """测试列出可用的提供商和模型"""
    providers = manager.list_available_providers()
    print(f"可用的 LLM 提供商: {providers}")
    
    default_provider = manager.config.llm_provider
    print(f"默认提供商: {default_provider}")
    
    for provider in providers:
        models = manager.list_available_models(provider)
        print(f"提供商 {provider} 的可用模型: {models}")


def test_simple_chat(manager: ModelManager):
    """测试简单聊天功能"""
    # 使用默认提供商和模型
    print("\n=== 测试简单聊天 (使用默认提供商和模型) ===")
    try:
        response = manager.chat(
            message="你好，请介绍一下你自己，不要超过100个字",
            system_prompt="你是一个简洁、友好的AI助手"
        )
        print(f"模型响应:\n{response}")
    except Exception as e:
        print(f"测试简单聊天出错: {e}")


def test_chat_with_specific_provider(manager: ModelManager):
    """测试使用特定提供商的聊天功能"""
    # 使用 openai_siliconflow 提供商
    provider = "openai_siliconflow"
    models = manager.list_available_models(provider)
    
    if not models:
        print(f"提供商 {provider} 没有可用的模型")
        return
    
    model = models[0]
    print(f"\n=== 测试特定提供商聊天 (提供商: {provider}, 模型: {model}) ===")
    
    try:
        response = manager.chat(
            message="请简要总结一下大语言模型的工作原理",
            system_prompt="你是一个简洁、专业的AI助手",
            provider=provider,
            model=model
        )
        print(f"模型响应:\n{response}")
    except Exception as e:
        print(f"测试特定提供商聊天出错: {e}")


def test_chat_with_history(manager: ModelManager):
    """测试使用历史记录的聊天功能"""
    print("\n=== 测试带历史记录的聊天 ===")
    
    messages = [
        {"role": "system", "content": "你是一个帮助用户学习Python编程的助手，提供简洁明了的回答。"},
        {"role": "user", "content": "什么是Python装饰器？"},
        {"role": "assistant", "content": "Python装饰器是一种函数，它接受另一个函数并扩展该函数的行为而不明确修改它的代码。装饰器是Python中函数式编程的一个强大工具，允许你在不改变函数代码的情况下添加功能。"},
        {"role": "user", "content": "能给我一个简单的装饰器例子吗？"}
    ]
    
    try:
        response = manager.chat_with_history(messages=messages)
        print(f"模型响应:\n{response}")
    except Exception as e:
        print(f"测试带历史记录的聊天出错: {e}")


def test_streaming_chat(manager: ModelManager):
    """测试流式聊天功能"""
    print("\n=== 测试流式聊天 ===")
    
    def stream_callback(chunk: str):
        print(chunk, end="", flush=True)
    
    try:
        print("流式输出: ", end="")
        manager.stream_callback(
            message="给我讲个简短的故事，不要超过200字",
            callback=stream_callback,
            system_prompt="你是一个创意故事讲述者"
        )
        print("\n流式输出完成")
    except Exception as e:
        print(f"\n测试流式聊天出错: {e}")


def test_convenience_functions():
    """测试便捷函数"""
    print("\n=== 测试便捷函数 ===")
    
    config_path = os.path.join("config.yaml")
    
    try:
        providers = list_available_providers(config_path)
        print(f"可用的LLM提供商: {providers}")
        
        default_provider = providers[0] if providers else None
        if (default_provider):
            models = list_available_models(default_provider, config_path)
            print(f"提供商 {default_provider} 的可用模型: {models}")
            
            if models:
                print("\n使用便捷函数进行简单聊天...")
                response = chat(
                    message="说一个编程的小技巧",
                    system_prompt="你是一个专业的编程导师",
                    provider=default_provider,
                    model=models[0],
                    config_path=config_path
                )
                print(f"模型响应:\n{response}")
    except Exception as e:
        print(f"测试便捷函数出错: {e}")


if __name__ == "__main__":
    print("开始测试 ModelManager 类...")
    
    try:
        # 初始化 ModelManager
        manager = test_model_manager_initialization()
        
        # 测试列出提供商和模型
        test_list_providers_and_models(manager)
        
        # 测试简单聊天功能
        test_simple_chat(manager)
        
        # 测试使用特定提供商的聊天功能
        test_chat_with_specific_provider(manager)
        
        # 测试使用历史记录的聊天功能
        test_chat_with_history(manager)
        
        # 测试流式聊天功能
        test_streaming_chat(manager)
        
        # 测试便捷函数
        test_convenience_functions()
        
        print("\n所有测试完成!")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")