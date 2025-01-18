import os
from typing import Dict, List, Optional
import yaml
from pathlib import Path

from .processor import PaperProcessor
from .agent import PaperAgent
from ..tools.markdown_converter import MarkdownConverter
from ..utils.output_formatter import OutputFormatter
from loguru import logger

class SmartPaper:
    """论文阅读和存档工具"""
    def __init__(self, config_file: str = None, output_format: str = 'markdown'):
        """初始化SmartPaper实例
        
        Args:
            config_file (str, optional): 配置文件路径
            output_format (str, optional): 输出格式 (markdown/csv/folder)
        """
        # 加载配置
        if config_file is None:
            config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     'config', 'config.yaml')
            
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
            
        self.config = self._load_config(config_file)
        logger.info(f"加载配置文件成功: {config_file}")
        
        # 初始化组件
        self.converter: MarkdownConverter = MarkdownConverter(config=self.config)
        self.processor: PaperProcessor = PaperProcessor(self.config)
        self.agent: PaperAgent = PaperAgent(self.config)
        self.output_formatter: OutputFormatter = OutputFormatter(self.config['output'])
        logger.info("初始化组件完成")
        
        # 设置输出格式
        self.output_format = output_format

    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件
        
        Args:
            config_file (str): 配置文件路径
            
        Returns:
            Dict: 配置信息
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"加载配置文件失败: {str(e)}")

    def process_paper(self, file_path: str, mode: str = 'prompt', prompt_name: str = None) -> Dict:
        """处理单个论文文件
        
        Args:
            file_path (str): 论文文件路径
            mode (str): 处理模式 ('prompt' 或 'agent')
            prompt_name (str, optional): 提示词名称
            
        Returns:
            Dict: 处理结果
        """
        try:
            # 转换PDF
            result = self.converter.convert(file_path)
            logger.info(f"转换PDF成功: {file_path}")
           
            # 根据模式处理
            if mode == 'prompt':
                analysis = self.processor.process(result['text_content'], prompt_name)
            else:
                analysis = self.agent.analyze(result['text_content'])
            
            # 格式化输出
            output = self.output_formatter.format(
                content=analysis,
                metadata=result['metadata'],
                format=self.output_format
            )
            
            return output
            
        except Exception as e:
            raise Exception(f"处理论文失败: {str(e)}")

    def process_directory(self, dir_path: str, mode: str = 'prompt', prompt_name: str = None) -> List[Dict]:
        """处理目录中的所有论文
        
        Args:
            dir_path (str): 目录路径
            mode (str): 处理模式 ('prompt' 或 'agent')
            prompt_name (str, optional): 提示词名称
            
        Returns:
            List[Dict]: 处理结果列表
        """
        results = []
        dir_path = Path(dir_path)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
            
        for file_path in dir_path.glob('*.pdf'):
            try:
                result = self.process_paper(str(file_path), mode, prompt_name)
                results.append(result)
            except Exception as e:
                print(f"处理文件 {file_path} 失败: {str(e)}")
                
        return results

    def process_paper_url(self, url: str, mode: str = 'prompt', prompt_name: str = None, description: str = None) -> Dict:
        """处理论文URL
        
        Args:
            url (str): 论文URL
            mode (str): 处理模式 ('prompt' 或 'agent')
            prompt_name (str, optional): 提示词名称
            description (str, optional): 论文描述
            
        Returns:
            Dict: 处理结果
        """
        try:
            # 下载并转换PDF
            logger.info(f"开始处理论文URL: {url}")
            result = self.converter.convert_url(url, description=description)
            logger.info("PDF转换完成，开始分析")
            
            # 根据模式处理
            if mode == 'prompt':
                analysis = self.processor.process(result['text_content'], prompt_name)
            else:
                analysis = self.agent.analyze(result['text_content'])
            logger.info(f"分析完成，使用模式: {mode}")
            
            # 格式化输出
            output = self.output_formatter.format(
                content=analysis,
                metadata=result['metadata'],
                format=self.output_format
            )
            
            return output
            
        except Exception as e:
            raise Exception(f"处理论文URL失败: {str(e)}")

    def set_api_key(self, api_key: str):
        """设置API密钥
        
        Args:
            api_key (str): API密钥
        """
        self.processor.set_api_key(api_key)
        self.agent.set_api_key(api_key)
        
    def reset_request_count(self):
        """重置所有组件的请求计数器"""
        self.processor.reset_request_count()
        if hasattr(self.agent, 'reset_request_count'):
            self.agent.reset_request_count() 