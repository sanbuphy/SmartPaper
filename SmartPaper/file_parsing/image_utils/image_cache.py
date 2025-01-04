"""
图片缓存类，主要用于将图片转换为base64编码并存储在缓存中
"""

import os
import base64
import time
from typing import Optional, Dict, Union
from diskcache import Cache


class ImageCache:
    """
    使用diskcache库实现的图片缓存系统，用于存储图片的base64编码
    
    主要功能：
    - 将图片转换为base64编码并存储
    - 从缓存中检索base64编码的图片
    - 管理缓存的生命周期
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化图片缓存系统
        
        Args:
            cache_dir: 缓存目录，如果为None则使用默认目录
            expire_seconds: 缓存过期时间(秒)，默认为7天(604800秒)
        """
        # 如果没有指定缓存目录，则在当前目录下创建默认目录
        if cache_dir is None:
            cache_dir = os.path.join("./image_cache")
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 初始化缓存
        self.cache = Cache(directory=cache_dir)

    def image_to_base64(self, image_path: str) -> str:
        """
        将图片转换为base64编码
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            str: 图片的base64编码字符串
        """
        with open(image_path, "rb") as img_file:
            # 读取图片文件并进行base64编码
            encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
            
            # 获取文件扩展名，用于构建data URI
            file_ext = os.path.splitext(image_path)[1].lstrip('.')
            if file_ext.lower() in ('jpg', 'jpeg'):
                file_ext = 'jpeg'
                
            # 返回完整的data URI
            return f"data:image/{file_ext};base64,{encoded_string}"
    
    def cache_image(self, image_path: str) -> str:
        """
        将图片转换为base64并存入缓存
        
        Args:
            image_path: 图片文件路径
            key: 缓存键名，如果为None则使用图片路径作为键
            
        Returns:
            str: 缓存的键名
        """
        # 如果未提供键名，则使用图片路径


        # 检查图片是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        key = os.path.splitext(os.path.basename(image_path))[0]


        # 转换为base64并存入缓存
        base64_data = self.image_to_base64(image_path)


        # 将base64数据和时间戳一起存储
        self.cache.set(
            key, 
             base64_data
        )
        
        return key
    
    def get_base64_image(self, key: str) -> Optional[str]:
        """
        从缓存中获取base64编码的图片
        
        Args:
            key: 缓存键名
            
        Returns:
            Optional[str]: base64编码的图片，如果不存在则返回None
        """
        # 从缓存中获取数据
        cached_data = self.cache.get(key)
        
        if cached_data is None:
            return None
            
        # 返回base64数据
        return cached_data
    
    def cache_multiple_images(self, image_paths: list, prefix: str = "") -> Dict[str, str]:
        """
        批量缓存多个图片
        
        Args:
            image_paths: 图片路径列表
            prefix: 缓存键名前缀
            
        Returns:
            Dict[str, str]: 图片路径到缓存键的映射
        """
        result = {}
        for i, path in enumerate(image_paths):
            key = f"{prefix}_{i}" if prefix else f"img_{i}_{os.path.basename(path)}"
            result[path] = self.cache_image(path, key)
        return result
    
    def clear_expired(self) -> int:
        """
        清理过期的缓存项
        
        Returns:
            int: 清理的缓存项数量
        """
        count = 0
        current_time = time.time()
        
        # 遍历缓存中的所有键
        for key in list(self.cache):
            cached_data = self.cache.get(key)
            if cached_data and isinstance(cached_data, dict):
                timestamp = cached_data.get("timestamp", 0)
                # 如果缓存项已过期，则删除它
                if current_time - timestamp > self.expire_seconds:
                    self.cache.delete(key)
                    count += 1
                    
        return count
    
    
    def close(self):
        """关闭缓存连接"""
        self.cache.close()
        
    def __enter__(self):
        """上下文管理器的进入方法"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器的退出方法，确保缓存被正确关闭"""
        self.close()


if __name__ == "__main__":
    # 测试代码
    key = "'ed89a02e85d34feab8bd1b1046ca8e0b'"  # 替换为实际的图片路径
    cache_dir = "./cache"  # 替换为实际的缓存目录
    image_path = "./image.png"

    with ImageCache(cache_dir=cache_dir) as cache:
        # 缓存图片
        key = cache.cache_image(image_path)
        print(f"缓存的键名: {key}")
        # 获取缓存的base64编码
        base64_data = cache.get_base64_image(key)
    print(base64_data)