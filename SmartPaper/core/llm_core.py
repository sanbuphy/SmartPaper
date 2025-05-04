"""
基于OpenAI API的对话模块，支持单轮对话和流式输出
"""

import os
from typing import List, Dict, Optional, Iterator, Callable, Union
import openai
from dotenv import load_dotenv

#  加载环境变量
load_dotenv()


class OpenAILLM:
    """
    OpenAI LLM对话类，使用OpenAI API进行单轮对话，支持流式输出
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 2048):
        """
        初始化OpenAI LLM对话类
        
        Args:
            api_key: OpenAI API密钥，如果为None，将从配置文件或环境变量中读取
            model: 使用的模型名称，默认为"gpt-3.5-turbo"
            base_url: OpenAI API基础URL，如果为None，将从配置文件或环境变量中读取
            temperature: 控制生成文本随机性的参数，范围 0-2，默认为 0.7。值越高表示输出越随机
            max_tokens: 生成文本的最大token数，默认为2048
        """
         
        # 尝试从环境变量获取API密钥和base_url
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            
        if base_url is None:
            base_url = os.environ.get("OPENAI_API_BASE")
            
        if api_key is None:
            raise ValueError("未提供OpenAI API密钥。请通过参数、配置文件或环境变量提供API密钥。")
            
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
            
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        
    def chat(self, message: str, system_prompt: str = "你是一个有用的AI助手。", stream: bool = False) -> Union[str, Iterator[str]]:
        """
        进行单轮对话
        
        Args:
            message: 用户的输入消息
            system_prompt: 系统提示，用于设置助手的行为
            stream: 是否使用流式输出，如果为True则返回一个迭代器
            
        Returns:
            如果stream=False，返回助手的完整回复字符串
            如果stream=True，返回一个迭代器，每次迭代返回回复的一部分
        """
        if stream:
            return self._chat_stream(message, system_prompt)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        reply = response.choices[0].message.content
        return reply
    
    def _chat_stream(self, message: str, system_prompt: str = "你是一个有用的AI助手。") -> Iterator[str]:
        """
        进行流式单轮对话，返回迭代器
        
        Args:
            message: 用户的输入消息
            system_prompt: 系统提示，用于设置助手的行为
            
        Returns:
            迭代器，每次迭代返回回复的一部分
        """
        stream_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            stream=True,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        
        for chunk in stream_response:
            if chunk.choices and len(chunk.choices) > 0:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content

    def chat_with_history(self, messages: List[Dict[str, str]], stream: bool = False) -> Union[str, Iterator[str]]:
        """
        使用对话历史进行对话
        
        Args:
            messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
            stream: 是否使用流式输出，如果为True则返回一个迭代器
            
        Returns:
            如果stream=False，返回助手的完整回复字符串
            如果stream=True，返回一个迭代器，每次迭代返回回复的一部分
        """
        if stream:
            return self._chat_with_history_stream(messages)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        reply = response.choices[0].message.content
        return reply
    
    def _chat_with_history_stream(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        """
        使用对话历史进行流式对话，返回迭代器
        
        Args:
            messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
            
        Returns:
            迭代器，每次迭代返回回复的一部分
        """
        stream_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        
        for chunk in stream_response:
            if chunk.choices and len(chunk.choices) > 0:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content

    def stream_callback(self, message: str, callback: Callable[[str], None], system_prompt: str = "你是一个有用的AI助手。") -> None:
        """
        使用回调函数处理流式响应
        
        Args:
            message: 用户输入的消息
            callback: 回调函数，接收流式输出的每个部分作为参数
            system_prompt: 系统提示，用于设置助手的行为
        """
        for chunk in self._chat_stream(message, system_prompt):
            callback(chunk)
    
    def stream_with_history_callback(self, messages: List[Dict[str, str]], callback: Callable[[str], None]) -> None:
        """
        使用回调函数处理带历史记录的流式响应
        
        Args:
            messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
            callback: 回调函数，接收流式输出的每个部分作为参数
        """
        for chunk in self._chat_with_history_stream(messages):
            callback(chunk)


# 便捷函数
def get_llm_response(
    message: str, 
    system_prompt: str = "你是一个有用的AI助手。", 
    api_key: Optional[str] = None, 
    model: str = "gpt-3.5-turbo", 
    base_url: Optional[str] = None,
    stream: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> Union[str, Iterator[str]]:
    """
    便捷函数，获取LLM的单次回复
    
    Args:
        message: 用户消息
        system_prompt: 系统提示
        api_key: OpenAI API密钥，如果为None，将从配置文件或环境变量中读取
        model: 使用的模型名称
        base_url: OpenAI API基础URL，如果为None，将从配置文件或环境变量中读取
        stream: 是否使用流式输出
        temperature: 控制生成文本随机性的参数，范围 0-2，默认为 0.7
        max_tokens: 生成文本的最大token数，默认为2048
        
    Returns:
        如果stream=False，返回LLM的完整回复字符串
        如果stream=True，返回一个迭代器，每次迭代返回回复的一部分
    """
    llm = OpenAILLM(api_key=api_key, model=model, base_url=base_url, temperature=temperature, max_tokens=max_tokens)
    return llm.chat(message=message, system_prompt=system_prompt, stream=stream)


def get_llm_response_with_callback(
    message: str, 
    callback: Callable[[str], None],
    system_prompt: str = "你是一个有用的AI助手。", 
    api_key: Optional[str] = None, 
    model: str = "gpt-3.5-turbo", 
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> None:
    """
    便捷函数，使用回调函数获取LLM的流式回复
    
    Args:
        message: 用户消息
        callback: 回调函数，接收流式输出的每个部分作为参数
        system_prompt: 系统提示
        api_key: OpenAI API密钥，如果为None，将从配置文件或环境变量中读取
        model: 使用的模型名称
        base_url: OpenAI API基础URL，如果为None，将从配置文件或环境变量中读取
        temperature: 控制生成文本随机性的参数，范围 0-2，默认为 0.7
        max_tokens: 生成文本的最大token数，默认为2048
    """
    llm = OpenAILLM(api_key=api_key, model=model, base_url=base_url, temperature=temperature, max_tokens=max_tokens)
    llm.stream_callback(message=message, callback=callback, system_prompt=system_prompt)


def get_llm_response_with_history_callback(
    messages: List[Dict[str, str]], 
    callback: Callable[[str], None],
    api_key: Optional[str] = None, 
    model: str = "gpt-3.5-turbo", 
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> None:
    """
    便捷函数，使用回调函数和对话历史获取LLM的流式回复
    
    Args:
        messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
        callback: 回调函数，接收流式输出的每个部分作为参数
        api_key: OpenAI API密钥，如果为None，将从配置文件或环境变量中读取
        model: 使用的模型名称
        base_url: OpenAI API基础URL，如果为None，将从配置文件或环境变量中读取
        temperature: 控制生成文本随机性的参数，范围 0-2，默认为 0.7
        max_tokens: 生成文本的最大token数，默认为2048
    """
    llm = OpenAILLM(api_key=api_key, model=model, base_url=base_url, temperature=temperature, max_tokens=max_tokens)
    llm.stream_with_history_callback(messages=messages, callback=callback)

