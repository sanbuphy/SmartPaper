from typing import Dict, Optional, Generator, List
from langchain.schema import HumanMessage, BaseMessage
from core.prompt_manager import get_prompt
from utils.llm_adapter import create_llm_adapter
from loguru import logger


class LLMWrapper:
    """这是一个LLM包装器，用于处理LLM相关的操作"""

    def __init__(self, config: Dict):
        """初始化处理器

        Args:
            config (Dict): 配置信息
        """
        self.config = config
        self.llm = create_llm_adapter(config["llm"])
        self.request_count = 0
        self.max_requests = config["llm"].get("max_requests", 10)

        # 打印当前使用的LLM配置信息
        provider = config["llm"]["provider"]
        model_index = config["llm"].get("default_model_index", 0)
        model = config["llm"][provider]["models"][model_index]

        logger.info("\n当前使用的LLM配置信息:")
        logger.info(f"- 提供商: {provider}")
        logger.info(f"- 模型: {model}\n")
        logger.info(f"初始化PaperProcessor完成，使用模型: {config['llm']['provider']}")

    def process_with_content(self, text: str, prompt_name: Optional[str] = None) -> Dict:
        """使用提示词处理已获取的文本内容

        Args:
            text (str): 要处理的文本内容
            prompt_name (Optional[str]): 提示词名称

        Returns:
            Dict: 处理结果

        Raises:
            Exception: 当超过最大请求次数时抛出异常
        """
        # 检查请求次数
        if self.request_count >= self.max_requests:
            raise Exception(f"已达到最大请求次数限制({self.max_requests}次)")

        # 获取提示词
        if prompt_name is None:
            prompt_name = self.config["prompts"]["default"]
        prompt_template = get_prompt(prompt_name)
        logger.info(f"使用提示词模板: {prompt_name}")

        # 填充提示词
        prompt = prompt_template.format(text=text)

        try:
            self.request_count += 1
            messages = [HumanMessage(content=prompt)]
            response = self.llm(messages)
            return {
                "result": response.content,
                "prompt_name": prompt_name,
                "request_count": self.request_count,
            }
        except Exception as e:
            raise Exception(f"LLM请求失败: {str(e)}")

    def _stream_chat(self, messages: List[BaseMessage]) -> Generator[str, None, None]:
        """流式处理消息

        Args:
            messages (List[BaseMessage]): 消息列表

        Yields:
            str: 流式输出的文本片段

        Raises:
            Exception: 当请求失败时抛出异常
        """
        try:
            for chunk in self.llm.stream(messages):
                yield chunk
        except Exception as e:
            raise Exception(f"LLM流式请求失败: {str(e)}")

    def process_stream_with_content(
        self, text: str, prompt_name: Optional[str] = None
    ) -> Generator[str, None, None]:
        """使用提示词流式处理已获取的文本内容

        Args:
            text (str): 要处理的文本内容
            prompt_name (Optional[str]): 提示词名称

        Yields:
            str: 流式输出的文本片段

        Raises:
            Exception: 当超过最大请求次数时抛出异常
        """
        # 检查请求次数
        if self.request_count >= self.max_requests:
            logger.error(f"已达到最大请求次数限制({self.max_requests}次)")
            raise Exception(f"已达到最大请求次数限制({self.max_requests}次)")

        try:
            self.request_count += 1

            # 获取提示词
            if prompt_name is None:
                prompt_name = self.config["prompts"]["default"]
            prompt_template = get_prompt(prompt_name)
            logger.info(f"使用提示词模板: {prompt_name}")

            # 填充提示词
            prompt = prompt_template.format(text=text)
            messages = [HumanMessage(content=prompt)]

            # 使用流式接口处理
            for chunk in self._stream_chat(messages):
                yield chunk

        except Exception as e:
            logger.error(f"LLM流式请求失败: {str(e)}")
            raise Exception(f"LLM流式请求失败: {str(e)}")

    def set_api_key(self, api_key: str):
        """设置API密钥

        Args:
            api_key (str): API密钥
        """
        self.llm.update_api_key(api_key)

    def reset_request_count(self):
        """重置请求计数器"""
        self.request_count = 0
