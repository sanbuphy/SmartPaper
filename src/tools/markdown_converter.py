import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import requests
import mimetypes
from markitdown import MarkItDown

class MarkdownConverter:
    """通用文档转Markdown转换器"""
    
    def __init__(self, config: Optional[Dict] = None, llm_client: Any = None, llm_model: str = None):
        """初始化转换器
        
        Args:
            config (Optional[Dict]): 配置信息
            llm_client (Any): LLM客户端,用于图像描述等高级功能
            llm_model (str): LLM模型名称
        """
        self.config = config or {}
        
        # 根据是否提供LLM客户端来初始化MarkItDown
        if llm_client and llm_model:
            self.md = MarkItDown(llm_client=llm_client, llm_model=llm_model)
        else:
            self.md = MarkItDown()
            
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
            
            # 提取元数据
            metadata = {
                'title': getattr(result, 'title', ''),
                'author': getattr(result, 'author', ''),
                'date': getattr(result, 'date', ''),
                'file_type': ext,
                'file_name': file_path.name,
                'file_size': os.path.getsize(file_path)
            }
            
            # 提取图片信息
            images = []
            if hasattr(result, 'images'):
                for img in result.images:
                    image_info = {
                        'path': img.get('path', ''),
                        'description': img.get('description', '')
                    }
                    images.append(image_info)
            
            return {
                'text_content': result.text_content,
                'metadata': metadata,
                'images': images
            }
        except Exception as e:
            raise Exception(f"文件转换失败: {str(e)}")

    def convert_url(self, url: str) -> Dict:
        """从URL下载并转换文件
        
        Args:
            url (str): 文件URL
            
        Returns:
            Dict: 包含转换结果的字典
        """
        try:
            # 下载文件
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # 获取文件类型
            content_type = response.headers.get('content-type', '')
            ext = mimetypes.guess_extension(content_type) or '.pdf'
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                temp_path = temp_file.name
            
            # 转换文件
            try:
                result = self.convert(temp_path)
                result['metadata']['url'] = url
                return result
            finally:
                # 清理临时文件
                os.unlink(temp_path)
                
        except Exception as e:
            raise Exception(f"URL文件转换失败: {str(e)}")
