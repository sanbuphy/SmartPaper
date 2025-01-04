from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
import zhipuai
from langchain.chat_models import ChatOpenAI

class BaseLLMAdapter(ABC):
    """LLM适配器基类"""
    
    @abstractmethod
    def __call__(self, messages: List[BaseMessage]) -> AIMessage:
        """调用LLM处理消息

        Args:
            messages (List[BaseMessage]): 消息列表

        Returns:
            AIMessage: AI响应消息
        """
        pass

    @abstractmethod
    def update_api_key(self, api_key: str):
        """更新API密钥

        Args:
            api_key (str): 新的API密钥
        """
        pass

class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化OpenAI适配器

        Args:
            config (Dict[str, Any]): OpenAI配置
        """
        self.config = config
        self.client = ChatOpenAI(
            api_key=config['api_key'],
            base_url=config.get('base_url'),  # 可选的自定义API端点
            model=config['model'],
            temperature=config['temperature'],
            max_tokens=config['max_tokens']
        )

    def __call__(self, messages: List[BaseMessage]) -> AIMessage:
        """调用OpenAI处理消息"""
        return self.client(messages)

    def update_api_key(self, api_key: str):
        """更新API密钥"""
        self.config['api_key'] = api_key
        self.client = ChatOpenAI(
            api_key=api_key,
            base_url=self.config.get('base_url'),
            model=self.config['model'],
            temperature=self.config['temperature'],
            max_tokens=self.config['max_tokens']
        )

class ZhipuChatAdapter(BaseLLMAdapter):
    """智谱AI适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化智谱AI适配器

        Args:
            config (Dict[str, Any]): 智谱AI配置
        """
        self.config = config
        zhipuai.api_key = config['api_key']
        self.model = config['model']
        self.temperature = config['temperature']
        self.max_tokens = config['max_tokens']

    def __call__(self, messages: List[BaseMessage]) -> AIMessage:
        """调用智谱AI处理消息"""
        # 转换消息格式
        zhipu_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                zhipu_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                zhipu_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                zhipu_messages.append({"role": "assistant", "content": msg.content})

        # 调用智谱AI API
        response = zhipuai.model_api.invoke(
            model=self.model,
            prompt=zhipu_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        if response['code'] != 200:
            raise Exception(f"智谱AI API调用失败: {response['msg']}")

        return AIMessage(content=response['data']['choices'][0]['content'])

    def update_api_key(self, api_key: str):
        """更新API密钥"""
        self.config['api_key'] = api_key
        zhipuai.api_key = api_key

def create_llm_adapter(config: Dict[str, Any]) -> BaseLLMAdapter:
    """创建LLM适配器

    Args:
        config (Dict[str, Any]): LLM配置

    Returns:
        BaseLLMAdapter: LLM适配器实例
    """
    provider = config['provider'].lower()
    if provider == 'openai':
        return OpenAIAdapter(config['openai'])
    elif provider == 'openai_deepseek':
        return OpenAIAdapter(config['openai_deepseek'])
    elif provider == 'openai_siliconflow':
        return OpenAIAdapter(config['openai_siliconflow'])
    elif provider == 'zhipuai':
        return ZhipuChatAdapter(config['zhipuai'])
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")