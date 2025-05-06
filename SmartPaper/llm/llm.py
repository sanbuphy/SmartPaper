"""
基于OpenAI API的对话模块，支持单轮对话和流式输出
"""

import os
import logging
from typing import List, Dict, Any, Optional, Iterator, Callable, Union
import openai

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAILLM:
    """
    OpenAI LLM对话类，使用OpenAI API进行单轮对话，支持流式输出
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None):
        """
        初始化OpenAI LLM对话类
        
        Args:
            api_key: OpenAI API密钥，如果为None，将从环境变量中读取
            model: 使用的模型名称，默认为"gpt-3.5-turbo"
            base_url: OpenAI API基础URL，如果为None，将从环境变量中读取
        """
        # 从环境变量获取API密钥和base_url
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            
        if base_url is None:
            base_url = os.environ.get("OPENAI_API_BASE")
            
        if api_key is None:
            raise ValueError("未提供OpenAI API密钥。请通过参数或环境变量提供API密钥。")
            
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        
        # 创建OpenAI客户端，支持自定义base_url
        client_args = {"api_key": api_key}
        if base_url:
            client_args["base_url"] = base_url
            logger.info(f"使用自定义API基础URL: {base_url}")
            
        self.client = openai.OpenAI(**client_args)
        logger.info(f"初始化OpenAI LLM，使用模型: {model}")
        
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
        try:
            logger.info(f"发送消息到OpenAI: {message[:50]}...")
            
            if stream:
                return self._chat_stream(message, system_prompt)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            
            reply = response.choices[0].message.content
            logger.info(f"收到OpenAI回复: {reply[:50]}...")
            return reply
            
        except Exception as e:
            logger.error(f"OpenAI API 调用出错: {str(e)}")
            raise RuntimeError(f"与LLM对话失败: {str(e)}")
    
    def _chat_stream(self, message: str, system_prompt: str = "你是一个有用的AI助手。") -> Iterator[str]:
        """
        进行流式单轮对话，返回迭代器
        
        Args:
            message: 用户的输入消息
            system_prompt: 系统提示，用于设置助手的行为
            
        Returns:
            迭代器，每次迭代返回回复的一部分
        """
        try:
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                stream=True
            )
            
            logger.info("开始接收流式响应...")
            
            for chunk in stream_response:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content is not None:
                        yield content
                        
            logger.info("流式响应接收完成")
            
        except Exception as e:
            logger.error(f"OpenAI API 流式调用出错: {str(e)}")
            raise RuntimeError(f"与LLM流式对话失败: {str(e)}")

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
        try:
            if stream:
                return self._chat_with_history_stream(messages)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            reply = response.choices[0].message.content
            return reply
            
        except Exception as e:
            logger.error(f"OpenAI API 调用出错: {str(e)}")
            raise RuntimeError(f"与LLM对话失败: {str(e)}")
    
    def _chat_with_history_stream(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        """
        使用对话历史进行流式对话，返回迭代器
        
        Args:
            messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
            
        Returns:
            迭代器，每次迭代返回回复的一部分
        """
        try:
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            logger.info("开始接收流式响应...")
            
            for chunk in stream_response:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content is not None:
                        yield content
                        
            logger.info("流式响应接收完成")
            
        except Exception as e:
            logger.error(f"OpenAI API 流式调用出错: {str(e)}")
            raise RuntimeError(f"与LLM流式对话失败: {str(e)}")

    def stream_callback(self, message: str, callback: Callable[[str], None], system_prompt: str = "你是一个有用的AI助手。") -> None:
        """
        使用回调函数处理流式响应
        
        Args:
            message: 用户输入的消息
            callback: 回调函数，接收流式输出的每个部分作为参数
            system_prompt: 系统提示，用于设置助手的行为
        """
        try:
            for chunk in self._chat_stream(message, system_prompt):
                callback(chunk)
        except Exception as e:
            logger.error(f"流式回调处理出错: {str(e)}")
            raise RuntimeError(f"流式回调处理出错: {str(e)}")
    
    def stream_with_history_callback(self, messages: List[Dict[str, str]], callback: Callable[[str], None]) -> None:
        """
        使用回调函数处理带历史记录的流式响应
        
        Args:
            messages: 对话历史，格式为[{"role": "system"/"user"/"assistant", "content": "消息内容"}, ...]
            callback: 回调函数，接收流式输出的每个部分作为参数
        """
        try:
            for chunk in self._chat_with_history_stream(messages):
                callback(chunk)
        except Exception as e:
            logger.error(f"流式回调处理出错: {str(e)}")
            raise RuntimeError(f"流式回调处理出错: {str(e)}")


# 便捷函数
def get_llm_response(
    message: str, 
    system_prompt: str = "你是一个有用的AI助手。", 
    api_key: Optional[str] = None, 
    model: str = "gpt-3.5-turbo", 
    base_url: Optional[str] = None,
    stream: bool = False
) -> Union[str, Iterator[str]]:
    """
    便捷函数，获取LLM的单次回复
    
    Args:
        message: 用户消息
        system_prompt: 系统提示
        api_key: OpenAI API密钥，如果为None，将从环境变量中读取
        model: 使用的模型名称
        base_url: OpenAI API基础URL，如果为None，将从环境变量中读取
        stream: 是否使用流式输出
        
    Returns:
        如果stream=False，返回LLM的完整回复字符串
        如果stream=True，返回一个迭代器，每次迭代返回回复的一部分
    """
    llm = OpenAILLM(api_key=api_key, model=model, base_url=base_url)
    return llm.chat(message=message, system_prompt=system_prompt, stream=stream)


def get_llm_response_with_callback(
    message: str, 
    callback: Callable[[str], None],
    system_prompt: str = "你是一个有用的AI助手。", 
    api_key: Optional[str] = None, 
    model: str = "gpt-3.5-turbo", 
    base_url: Optional[str] = None
) -> None:
    """
    便捷函数，使用回调函数获取LLM的流式回复
    
    Args:
        message: 用户消息
        callback: 回调函数，接收流式输出的每个部分作为参数
        system_prompt: 系统提示
        api_key: OpenAI API密钥，如果为None，将从环境变量中读取
        model: 使用的模型名称
        base_url: OpenAI API基础URL，如果为None，将从环境变量中读取
    """
    llm = OpenAILLM(api_key=api_key, model=model, base_url=base_url)
    llm.stream_callback(message=message, callback=callback, system_prompt=system_prompt)