import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import requests
import mimetypes
from markitdown import MarkItDown
from loguru import logger

class MarkdownConverter:
    """通用文档转Markdown转换器"""
    
    def __init__(self, llm_client: Any = None, llm_model: str = None):
        """初始化转换器
        
        Args:
            llm_client (Any): LLM客户端,用于图像描述等高级功能
            llm_model (str): LLM模型名称
        """
        # 根据是否提供LLM客户端来初始化MarkItDown
        if llm_client and llm_model:
            self.md = MarkItDown(llm_client=llm_client, llm_model=llm_model)
        else:
            self.md = MarkItDown()
        logger.info("初始化MarkdownConverter完成")
            
        # 支持的文件类型
        self.supported_extensions = {
            '.pdf', '.docx', '.pptx', '.xlsx', 
            '.jpg', '.jpeg', '.png',
            '.txt', '.md', '.csv', '.json', 
            '.yaml', '.yml', '.html', '.htm',
            '.zip', '.mp3', '.wav', '.xml'
        }

    def convert(self, file_path: str) -> Dict:
        """转换文件为Markdown
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Dict: 包含转换结果的字典
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        ext = file_path.suffix.lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"不支持的文件类型: {ext}")
            
        try:
            result = self.md.convert(str(file_path))
            
            return {
                'text_content': result.text_content,
                'metadata': {},
                'images': []
            }
        except Exception as e:
            raise Exception(f"文件转换失败: {str(e)}")

    def convert_url(self, url: str, description: str = None) -> Dict:
        """从URL下载并转换文件
        
        Args:
            url (str): 文件URL
            description (str, optional): 论文描述
            
        Returns:
            Dict: 包含转换结果的字典
        """
        try:
            # 判断是否为PDF文件
            is_arxiv = "arxiv.org" in url.lower()
            
            if is_arxiv:
                # 创建temp目录(如果不存在)
                temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp')
                os.makedirs(temp_dir, exist_ok=True)
                
                # 从URL提取文件名
                arxiv_id = url.split('/')[-1]
                if not arxiv_id.endswith('.pdf'):
                    arxiv_id += '.pdf'
                temp_path = os.path.join(temp_dir, arxiv_id)
                
                # 检查是否已存在同名文件
                if not os.path.exists(temp_path):
                    # 下载PDF文件
                    logger.info(f"开始下载PDF: {url}")
                    response = requests.get(url)
                    response.raise_for_status()
                    
                    with open(temp_path, 'wb') as f:
                        f.write(response.content)
                    logger.info("PDF下载完成")
                
                # 转换PDF文件
                result = self.convert(temp_path)
                logger.info("PDF转换完成")
                
                # 处理文本内容
                text_content = result['text_content']
                if "References" in text_content:
                    text_content = text_content.split("References")[0]
                text_content = "\n".join([line for line in text_content.split("\n") if line.strip()])
                
                # 更新结果
                result['text_content'] = text_content
                result['metadata']['url'] = url
                if description:
                    result['metadata']['description'] = description
                return result
                
            else:
                # 获取网页内容
                response = requests.get(url)
                response.raise_for_status()
                
                # 使用MarkItDown转换HTML
                result = response.text
                
                # 构建返回结果
                metadata = {
                    'title': url.split('/')[-1],
                    'url': url,
                    'file_type': 'html'
                }
                
                return {
                    'text_content': result,
                    'metadata': metadata,
                    'images': []
                }
                
        except Exception as e:
            raise Exception(f"URL转换失败: {str(e)}")