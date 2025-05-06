"""
PDF解析结果缓存模块

使用diskcache库实现PDF解析结果的持久化缓存，避免重复处理相同的PDF文件
"""

import os
import hashlib
import logging
from typing import Optional, Dict, Any, Tuple, Union
from diskcache import Cache

logger = logging.getLogger(__name__)

class PDFCache:
    """
    PDF缓存管理器
    
    用于缓存PDF到Markdown的转换结果，避免重复处理
    """
    
    def __init__(self, pdf_cache_dir: Optional[str] = None, namespace: str = "default"):
        """
        初始化PDF缓存管理器
        
        Args:
            cache_dir: PDF解析结果缓存目录，默认为'./data/caches/pdf_cache/{namespace}'
                      注意：这是存储PDF解析结果的缓存，不是图片缓存
            namespace: 缓存命名空间，用于隔离不同用途的缓存
        """
        if pdf_cache_dir is None:
            # 默认缓存目录
            pdf_cache_dir = os.path.join("./data", "caches", "pdf_cache")
            
        # 确保缓存目录存在
        os.makedirs(pdf_cache_dir, exist_ok=True)
        
        # 使用命名空间细分缓存
        self.namespace = namespace
        
        # 在基本缓存目录下创建命名空间子目录
        namespace_dir = os.path.join(pdf_cache_dir, namespace)
        
        # 初始化diskcache
        self.cache = Cache(namespace_dir)
        logger.info(f"PDF缓存已初始化，缓存目录: {namespace_dir}，命名空间: {namespace}")
        
    def get_cache_key(
        self, 
        pdf_path: str, 
        converter_type: str, 
        params: Dict[str, Any]
    ) -> str:
        """
        生成缓存键
        
        根据PDF文件路径、转换器类型和处理参数生成唯一的缓存键
        
        Args:
            pdf_path: PDF文件路径
            converter_type: 转换器类型，如'fitz'或'fitz_with_image'
            params: 处理参数
            
        Returns:
            缓存键字符串
        """
        # 获取文件大小和最后修改时间，用于确保文件未被修改
        file_stat = os.stat(pdf_path)
        file_size = file_stat.st_size
        file_mtime = file_stat.st_mtime
        
        # 准备用于哈希的键信息
        key_info = {
            "path": pdf_path,
            "size": file_size,
            "mtime": file_mtime,
            "converter": converter_type,
            "params": params,
            "namespace": self.namespace  # 将命名空间纳入哈希计算
        }
        
        # 转换为字符串并计算哈希
        key_str = str(key_info)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(
        self, 
        pdf_path: str, 
        converter_type: str, 
        params: Dict[str, Any]
    ) -> Optional[Union[str, Tuple[str, Dict[str, Any]]]]:
        """
        从缓存获取转换结果
        
        Args:
            pdf_path: PDF文件路径
            converter_type: 转换器类型
            params: 转换参数
            
        Returns:
            缓存的Markdown文本，如果缓存不存在则返回None
        """
        # 生成缓存键
        cache_key = self.get_cache_key(pdf_path, converter_type, params)
        
        # 从缓存中获取结果
        result = self.cache.get(cache_key)
        
        if result:
            logger.info(f"PDF处理结果缓存命中: {pdf_path} (命名空间: {self.namespace})")
            return result
        else:
            logger.info(f"PDF处理结果缓存未命中: {pdf_path} (命名空间: {self.namespace})")
            return None
    
    def set(
        self, 
        pdf_path: str, 
        converter_type: str, 
        params: Dict[str, Any], 
        result: Union[str, Tuple[str, Dict[str, Any]]]
    ) -> bool:
        """
        将转换结果存入缓存
        
        Args:
            pdf_path: PDF文件路径
            converter_type: 转换器类型
            params: 转换参数
            result: 转换结果(Markdown文本)
            
        Returns:
            bool: 是否成功缓存
        """
        # 生成缓存键
        cache_key = self.get_cache_key(pdf_path, converter_type, params)
        
        # 存储到缓存
        try:
            self.cache.set(cache_key, result)
            logger.info(f"PDF处理结果已缓存: {pdf_path} (命名空间: {self.namespace})")
            return True
        except Exception as e:
            logger.error(f"缓存PDF处理结果失败: {e}")
            return False
            
    def get_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        通过arXiv论文ID从缓存获取结果
        
        Args:
            paper_id: arXiv论文ID
            
        Returns:
            缓存的信息，包含PDF路径和元数据，如果缓存不存在则返回None
        """
        cache_key = f"arxiv_paper_{paper_id}"
        result = self.cache.get(cache_key)
        
        if result:
            logger.info(f"论文缓存命中: {paper_id} (命名空间: {self.namespace})")
            return result
        else:
            logger.info(f"论文缓存未命中: {paper_id} (命名空间: {self.namespace})")
            return None
            
    def set_by_paper_id(self, paper_id: str, data: Dict[str, Any]) -> bool:
        """
        通过arXiv论文ID存储缓存
        
        Args:
            paper_id: arXiv论文ID
            data: 要缓存的数据，通常包含PDF路径和元数据
            
        Returns:
            bool: 是否成功缓存
        """
        cache_key = f"arxiv_paper_{paper_id}"
        
        try:
            self.cache.set(cache_key, data)
            logger.info(f"论文已缓存: {paper_id} (命名空间: {self.namespace})")
            return True
        except Exception as e:
            logger.error(f"缓存论文失败: {e}")
            return False
    
    def clear(self) -> int:
        """
        清除所有缓存
        
        Returns:
            清除的缓存项数量
        """
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"已清除{count}个PDF处理结果缓存 (命名空间: {self.namespace})")
        return count
    
    def close(self) -> None:
        """
        关闭缓存
        """
        self.cache.close()
        logger.info(f"PDF缓存已关闭 (命名空间: {self.namespace})")
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
