from typing import Dict, Optional
from langchain_community.chat_models import ChatOpenAI
from ..prompts.prompt_library import get_prompt
from loguru import logger

class PaperProcessor:
    """论文处理器"""
    
    def __init__(self, config: Dict):
        """初始化处理器
        
        Args:
            config (Dict): 配置信息
        """
        self.config = config
        self.llm = self._init_llm()
        self.request_count = 0
        self.max_requests = config['llm'].get('max_requests', 10)
        logger.info(f"初始化PaperProcessor完成，使用模型: {config['llm']['provider']}")
        
    def _init_llm(self) -> ChatOpenAI:
        """初始化LLM模型"""
        provider = self.config['llm']['provider']
        llm_config = self.config['llm'][provider]
        
        return ChatOpenAI(
            api_key=llm_config['api_key'],
            base_url=llm_config.get('base_url'),
            model=llm_config['model'],
            temperature=llm_config['temperature'],
            max_tokens=llm_config['max_tokens']
        )
        
    def process(self, text: str, prompt_name: Optional[str] = None) -> Dict:
        """使用提示词处理文本
        
        Args:
            text (str): 要处理的文本
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
            prompt_name = self.config['prompts']['default']
        prompt_template = get_prompt(prompt_name)
        logger.info(f"使用提示词模板: {prompt_name}")
        
        # 填充提示词
        prompt = prompt_template.format(text=text)
        
        try:
            self.request_count += 1
            response = self.llm.predict(prompt)
            return {
                'result': response,
                'prompt_name': prompt_name,
                'request_count': self.request_count
            }
        except Exception as e:
            raise Exception(f"LLM请求失败: {str(e)}")
        
    def set_api_key(self, api_key: str):
        """设置API密钥
        
        Args:
            api_key (str): API密钥
        """
        self.llm.api_key = api_key
        
    def reset_request_count(self):
        """重置请求计数器"""
        self.request_count = 0 