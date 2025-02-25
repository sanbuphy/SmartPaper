from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
import zhipuai
from langchain_community.chat_models import ChatOpenAI


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
    def stream(self, messages: List[BaseMessage]):
        """流式调用LLM处理消息

        Args:
            messages (List[BaseMessage]): 消息列表

        Yields:
            str: 流式输出的文本片段
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

        # 根据 default_model_index 选择模型
        if "models" in config:
            try:
                model_index = config.get("default_model_index", 0)
                if not 0 <= model_index < len(config["models"]):
                    raise ValueError(
                        f"default_model_index {model_index} 超出模型列表范围 [0, {len(config['models'])-1}]"
                    )
                selected_model = config["models"][model_index]
            except IndexError:
                raise ValueError(
                    f"default_model_index {model_index} 超出模型列表范围 [0, {len(config['models'])-1}]"
                )
        else:
            selected_model = config["model"]

        self.client = ChatOpenAI(
            api_key=config["api_key"],
            base_url=config.get("base_url"),  # 可选的自定义API端点
            model=selected_model,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            streaming=False,
        )
        self.stream_client = ChatOpenAI(
            api_key=config["api_key"],
            base_url=config.get("base_url"),
            model=selected_model,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            streaming=True,
        )

    def __call__(self, messages: List[BaseMessage]) -> AIMessage:
        """调用OpenAI处理消息"""
        return self.client(messages)

    def stream(self, messages: List[BaseMessage]):
        """流式调用OpenAI处理消息"""
        for chunk in self.stream_client.stream(messages):
            if chunk.content:
                yield chunk.content

    def update_api_key(self, api_key: str):
        """更新API密钥"""
        self.config["api_key"] = api_key
        self.client = ChatOpenAI(
            api_key=api_key,
            base_url=self.config.get("base_url"),
            model=self.config["model"],
            temperature=self.config["temperature"],
            max_tokens=self.config["max_tokens"],
            streaming=False,
        )
        self.stream_client = ChatOpenAI(
            api_key=api_key,
            base_url=self.config.get("base_url"),
            model=self.config["model"],
            temperature=self.config["temperature"],
            max_tokens=self.config["max_tokens"],
            streaming=True,
        )


class ZhipuChatAdapter(BaseLLMAdapter):
    """智谱AI适配器"""

    def __init__(self, config: Dict[str, Any]):
        """初始化智谱AI适配器

        Args:
            config (Dict[str, Any]): 智谱AI配置
        """
        self.config = config
        zhipuai.api_key = config["api_key"]

        # 根据 default_model_index 选择模型
        if "models" in config:
            try:
                model_index = config.get("default_model_index", 0)
                if not 0 <= model_index < len(config["models"]):
                    raise ValueError(
                        f"default_model_index {model_index} 超出模型列表范围 [0, {len(config['models'])-1}]"
                    )
                self.model = config["models"][model_index]
            except IndexError:
                raise ValueError(
                    f"default_model_index {model_index} 超出模型列表范围 [0, {len(config['models'])-1}]"
                )
        else:
            self.model = config["model"]

        self.temperature = config["temperature"]
        self.max_tokens = config["max_tokens"]

    def __call__(self, messages: List[BaseMessage]) -> AIMessage:
        """调用智谱AI处理消息"""
        zhipu_messages = self._convert_messages(messages)
        response = zhipuai.model_api.invoke(
            model=self.model,
            prompt=zhipu_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        if response["code"] != 200:
            raise Exception(f"智谱AI API调用失败: {response['msg']}")

        return AIMessage(content=response["data"]["choices"][0]["content"])

    def stream(self, messages: List[BaseMessage]):
        """流式调用智谱AI处理消息"""
        zhipu_messages = self._convert_messages(messages)
        response = zhipuai.model_api.sse_invoke(
            model=self.model,
            prompt=zhipu_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        for event in response.events():
            if event.event == "add":
                yield event.data
            elif event.event == "error" or event.event == "interrupted":
                raise Exception(f"智谱AI流式调用失败: {event.data}")

    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict]:
        """转换消息格式"""
        zhipu_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                zhipu_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                zhipu_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                zhipu_messages.append({"role": "assistant", "content": msg.content})
        return zhipu_messages

    def update_api_key(self, api_key: str):
        """更新API密钥"""
        self.config["api_key"] = api_key
        zhipuai.api_key = api_key


def create_llm_adapter(config: Dict[str, Any]) -> BaseLLMAdapter:
    """创建LLM适配器

    Args:
        config (Dict[str, Any]): LLM配置

    Returns:
        BaseLLMAdapter: LLM适配器实例
    """
    provider = config["provider"].lower()
    if provider == "openai":
        return OpenAIAdapter(config["openai"])
    elif provider == "openai_deepseek":
        return OpenAIAdapter(config["openai_deepseek"])
    elif provider == "openai_siliconflow":
        return OpenAIAdapter(config["openai_siliconflow"])
    elif provider == "openai_kimi":
        return OpenAIAdapter(config["openai_kimi"])
    elif provider == "openai_doubao":
        return OpenAIAdapter(config["openai_doubao"])
    elif provider == "zhipuai":
        return ZhipuChatAdapter(config["zhipuai"])
    provider = config["provider"].lower()

    if provider == "openai":
        return OpenAIAdapter(config["openai"])
    elif provider == "openai_deepseek":
        return OpenAIAdapter(config["openai_deepseek"])
    elif provider == "openai_siliconflow":
        return OpenAIAdapter(config["openai_siliconflow"])
    elif provider == "openai_kimi":
        return OpenAIAdapter(config["openai_kimi"])
    elif provider == "openai_doubao":
        return OpenAIAdapter(config["openai_doubao"])
    elif provider == "zhipuai":
        return ZhipuChatAdapter(config["zhipuai"])
    elif provider == "ai_studio":
        return OpenAIAdapter(config["ai_studio"])
    elif provider == "ai_studio_fast_deploy":
        return OpenAIAdapter(config["ai_studio_fast_deploy"])
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")
