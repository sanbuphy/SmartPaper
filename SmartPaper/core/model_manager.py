"""
统一LLM调用管理器，结合配置系统支持多种模型和提供商的调用
"""

import os
from typing import Dict, List, Optional, Iterator, Callable, Union, Any, Type
import importlib.util
import inspect

from SmartPaper.core.config import Config
from SmartPaper.core.llm_core import OpenAILLM


class ModelManager:
    """
    模型管理器类，负责加载配置并根据配置调用不同的LLM提供商
    
    支持动态切换模型和提供商，提供统一的对话接口
    """
    
    # LLM提供商类映射
    PROVIDER_CLASSES = {
        "openai": OpenAILLM,
        # 可以在这里添加其他提供商的类，如 "anthropic": AnthropicLLM
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化模型管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config = Config(config_path=config_path)
        self.config_path = config_path
        self._llm_instances = {}  # 缓存不同提供商和模型的实例
        
    def get_llm(self, provider: Optional[str] = None, model: Optional[str] = None) -> Any:
        """
        获取指定提供商和模型的LLM实例
        
        Args:
            provider: LLM提供商名称，如果为None则使用配置中的默认值
            model: 模型名称，如果为None则使用配置中的默认值
            
        Returns:
            对应提供商和模型的LLM实例
        
        Raises:
            ValueError: 如果提供商不支持或配置缺失
        """
        # 确定提供商
        if provider is None:
            provider = self.config.llm_provider
        
        # 确定模型
        if model is None:
            model = self.config.default_model
        
        # 如果模型仍为None，尝试使用提供商配置中的第一个模型
        if model is None:
            models = self.config.get(f'llm.{provider}.models', [])
            if models:
                model = models[0]
            else:
                # 对于OpenAI，如果没有配置模型，使用默认值
                if provider == 'openai':
                    model = "gpt-3.5-turbo"
                else:
                    raise ValueError(f"未找到提供商 '{provider}' 的可用模型")
        
        # 创建缓存键
        cache_key = f"{provider}:{model}"
        
        # 如果缓存中已有实例，直接返回
        if cache_key in self._llm_instances:
            return self._llm_instances[cache_key]
        
        # 获取提供商特定配置
        provider_config = self.config.get(f'llm.{provider}', {})
        
        # 检查配置是否存在
        if not provider_config:
            raise ValueError(f"提供商 '{provider}' 的配置信息不存在")
            
        # 检查是否有API key
        api_key = provider_config.get('api_key')
        if not api_key:
            raise ValueError(f"提供商 '{provider}' 缺少API key")
        
        # 获取提供商类 - 动态处理各种提供商
        # 默认使用OpenAI类处理兼容OpenAI接口的服务
        provider_class = None
        
        # 检查是否是原生支持的提供商
        if provider in self.PROVIDER_CLASSES:
            provider_class = self.PROVIDER_CLASSES[provider]
        # 检查提供商名称是否包含"openai"，如openai_siliconflow
        elif "openai" in provider.lower():
            provider_class = OpenAILLM
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
        
        # 准备初始化参数
        init_params = {
            'api_key': api_key,
            'model': model
        }
        
        # 如果有base_url，添加到初始化参数
        base_url = provider_config.get('base_url')
        if base_url:
            init_params['base_url'] = base_url
        
        # 添加其他可能的参数
        if 'temperature' in provider_config:
            init_params['temperature'] = provider_config.get('temperature')
        
        if 'max_tokens' in provider_config:
            init_params['max_tokens'] = provider_config.get('max_tokens')
        
        # 创建实例
        instance = provider_class(**init_params)
        
        # 缓存并返回
        self._llm_instances[cache_key] = instance
        return instance
        
    def chat(
        self, 
        message: str, 
        system_prompt: str = "你是一个有用的AI助手。", 
        provider: Optional[str] = None, 
        model: Optional[str] = None,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """
        进行单轮对话，自动选择配置中的提供商和模型
        
        Args:
            message: 用户的输入消息
            system_prompt: 系统提示，用于设置助手的行为
            provider: LLM提供商，如果为None则使用配置中的默认值
            model: 模型名称，如果为None则使用配置中的默认值
            stream: 是否使用流式输出
            
        Returns:
            如果stream=False，返回助手的完整回复字符串
            如果stream=True，返回一个迭代器，每次迭代返回回复的一部分
        """
        llm = self.get_llm(provider, model)
        
        # 根据实例类型调用相应的方法
        if isinstance(llm, OpenAILLM):
            return llm.chat(message=message, system_prompt=system_prompt, stream=stream)
        
        # 可以在这里添加对其他LLM类型的支持
        # elif isinstance(llm, AnthropicLLM):
        #     return llm.generate(message=message, system_prompt=system_prompt, stream=stream)
        
        # 默认行为
        raise TypeError(f"不支持的LLM类型: {type(llm)}")
    
    def chat_with_history(
        self, 
        messages: List[Dict[str, str]], 
        provider: Optional[str] = None, 
        model: Optional[str] = None,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """
        使用对话历史进行对话
        
        Args:
            messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
            provider: LLM提供商，如果为None则使用配置中的默认值
            model: 模型名称，如果为None则使用配置中的默认值
            stream: 是否使用流式输出
            
        Returns:
            如果stream=False，返回助手的完整回复字符串
            如果stream=True，返回一个迭代器，每次迭代返回回复的一部分
        """
        llm = self.get_llm(provider, model)
        
        # 根据实例类型调用相应的方法
        if isinstance(llm, OpenAILLM):
            return llm.chat_with_history(messages=messages, stream=stream)
        
        # 可以在这里添加对其他LLM类型的支持
        # elif isinstance(llm, AnthropicLLM):
        #     return llm.chat_with_history(messages=messages, stream=stream)
        
        # 默认行为
        raise TypeError(f"不支持的LLM类型: {type(llm)}")
    
    def stream_callback(
        self, 
        message: str, 
        callback: Callable[[str], None], 
        system_prompt: str = "你是一个有用的AI助手。", 
        provider: Optional[str] = None, 
        model: Optional[str] = None
    ) -> None:
        """
        使用回调函数处理流式响应
        
        Args:
            message: 用户输入的消息
            callback: 回调函数，接收流式输出的每个部分作为参数
            system_prompt: 系统提示，用于设置助手的行为
            provider: LLM提供商，如果为None则使用配置中的默认值
            model: 模型名称，如果为None则使用配置中的默认值
        """
        llm = self.get_llm(provider, model)
        
        # 根据实例类型调用相应的方法
        if isinstance(llm, OpenAILLM):
            llm.stream_callback(message=message, callback=callback, system_prompt=system_prompt)
        # 可以在这里添加对其他LLM类型的支持
        else:
            raise TypeError(f"不支持的LLM类型: {type(llm)}")
    
    def stream_with_history_callback(
        self, 
        messages: List[Dict[str, str]], 
        callback: Callable[[str], None],
        provider: Optional[str] = None, 
        model: Optional[str] = None
    ) -> None:
        """
        使用回调函数处理带历史记录的流式响应
        
        Args:
            messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
            callback: 回调函数，接收流式输出的每个部分作为参数
            provider: LLM提供商，如果为None则使用配置中的默认值
            model: 模型名称，如果为None则使用配置中的默认值
        """
        llm = self.get_llm(provider, model)
        
        # 根据实例类型调用相应的方法
        if isinstance(llm, OpenAILLM):
            llm.stream_with_history_callback(messages=messages, callback=callback)
        # 可以在这里添加对其他LLM类型的支持
        else:
            raise TypeError(f"不支持的LLM类型: {type(llm)}")
    
    def list_available_providers(self) -> List[str]:
        """
        列出所有可用的LLM提供商
        
        Returns:
            提供商名称列表
        """
        # 从配置文件中寻找所有有API key的提供商
        available_providers = []
        llm_config = self.config.get('llm', {})
        
        for provider_name, provider_config in llm_config.items():
            # 跳过非提供商配置项
            if isinstance(provider_config, dict) and 'api_key' in provider_config:
                api_key = provider_config.get('api_key')
                base_url = provider_config.get('base_url', '')
                
                # 如果是OpenAI，只要有API key就可用
                if provider_name == 'openai' and api_key:
                    available_providers.append(provider_name)
                # 对于其他提供商，需要同时有API key和base_url
                elif api_key and base_url:
                    available_providers.append(provider_name)
        
        return available_providers if available_providers else ["openai"]
    
    def list_available_models(self, provider: Optional[str] = None) -> List[str]:
        """
        列出指定提供商的可用模型
        
        Args:
            provider: LLM提供商名称，如果为None则使用配置中的默认值
            
        Returns:
            可用模型名称列表
        """
        if provider is None:
            provider = self.config.llm_provider
        
        return self.config.get(f'llm.{provider}.models', [])
    
    def register_provider(self, name: str, provider_class: Type):
        """
        注册新的LLM提供商类
        
        Args:
            name: 提供商名称
            provider_class: 提供商对应的类
        """
        self.PROVIDER_CLASSES[name] = provider_class
        
    def clear_cache(self):
        """清除LLM实例缓存"""
        self._llm_instances.clear()
        
    def get_model_context_length(self, provider: str, model: str) -> int:
        """
        获取指定模型的最大上下文长度
        
        Args:
            provider: 提供商名称
            model: 模型名称
            
        Returns:
            模型的最大上下文长度，默认为32768
        """
        from SmartPaper.core.config import Config
        
        # 从配置中获取上下文长度
        config = Config(self.config_path)
        return config.get_model_context_length(provider, model)

# 便捷函数

def chat(
    message: str, 
    system_prompt: str = "你是一个有用的AI助手。", 
    provider: Optional[str] = None, 
    model: Optional[str] = None,
    stream: bool = False,
    config_path: Optional[str] = None
) -> Union[str, Iterator[str]]:
    """
    便捷函数，进行单轮对话
    
    Args:
        message: 用户消息
        system_prompt: 系统提示
        provider: LLM提供商，如果为None则使用配置中的默认值
        model: 模型名称，如果为None则使用配置中的默认值
        stream: 是否使用流式输出
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        如果stream=False，返回助手的完整回复字符串
        如果stream=True，返回一个迭代器，每次迭代返回回复的一部分
    """
    manager = ModelManager(config_path)
    return manager.chat(
        message=message, 
        system_prompt=system_prompt, 
        provider=provider,
        model=model,
        stream=stream
    )


def chat_with_history(
    messages: List[Dict[str, str]], 
    provider: Optional[str] = None, 
    model: Optional[str] = None,
    stream: bool = False,
    config_path: Optional[str] = None
) -> Union[str, Iterator[str]]:
    """
    便捷函数，使用对话历史进行对话
    
    Args:
        messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
        provider: LLM提供商，如果为None则使用配置中的默认值
        model: 模型名称，如果为None则使用配置中的默认值
        stream: 是否使用流式输出
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        如果stream=False，返回助手的完整回复字符串
        如果stream=True，返回一个迭代器，每次迭代返回回复的一部分
    """
    manager = ModelManager(config_path)
    return manager.chat_with_history(
        messages=messages,
        provider=provider,
        model=model,
        stream=stream
    )


def stream_callback(
    message: str, 
    callback: Callable[[str], None], 
    system_prompt: str = "你是一个有用的AI助手。", 
    provider: Optional[str] = None, 
    model: Optional[str] = None,
    config_path: Optional[str] = None
) -> None:
    """
    便捷函数，使用回调函数处理流式响应
    
    Args:
        message: 用户输入的消息
        callback: 回调函数，接收流式输出的每个部分作为参数
        system_prompt: 系统提示，用于设置助手的行为
        provider: LLM提供商，如果为None则使用配置中的默认值
        model: 模型名称，如果为None则使用配置中的默认值
        config_path: 配置文件路径，如果为None则使用默认路径
    """
    manager = ModelManager(config_path)
    manager.stream_callback(
        message=message,
        callback=callback,
        system_prompt=system_prompt,
        provider=provider,
        model=model
    )


def stream_with_history_callback(
    messages: List[Dict[str, str]], 
    callback: Callable[[str], None],
    provider: Optional[str] = None, 
    model: Optional[str] = None,
    config_path: Optional[str] = None
) -> None:
    """
    便捷函数，使用回调函数和对话历史处理流式响应
    
    Args:
        messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
        callback: 回调函数，接收流式输出的每个部分作为参数
        provider: LLM提供商，如果为None则使用配置中的默认值
        model: 模型名称，如果为None则使用配置中的默认值
        config_path: 配置文件路径，如果为None则使用默认路径
    """
    manager = ModelManager(config_path)
    manager.stream_with_history_callback(
        messages=messages,
        callback=callback,
        provider=provider,
        model=model
    )


def list_available_providers(config_path: Optional[str] = None) -> List[str]:
    """
    便捷函数，列出所有可用的LLM提供商
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        提供商名称列表
    """
    manager = ModelManager(config_path)
    return manager.list_available_providers()


def list_available_models(provider: Optional[str] = None, config_path: Optional[str] = None) -> List[str]:
    """
    便捷函数，列出指定提供商的可用模型
    
    Args:
        provider: LLM提供商名称，如果为None则使用配置中的默认值
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        可用模型名称列表
    """
    manager = ModelManager(config_path)
    return manager.list_available_models(provider)