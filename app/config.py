"""
应用配置管理模块

管理SmartPaper应用的各种配置，包括缓存目录等
"""

import os
from pathlib import Path
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 基础目录 - 默认使用用户主目录下的.smartpaper文件夹
BASE_DIR = os.path.expanduser(os.path.join("./data", "smartpaper"))

# 确保基础目录存在
os.makedirs(BASE_DIR, exist_ok=True)

# 各种缓存目录
CACHE_DIRS = {
    # PDF解析结果缓存目录
    "pdf_cache": os.path.join(BASE_DIR, "pdf_cache"),
    
    # 图片缓存目录
    "images_cache": os.path.join(BASE_DIR, "images_cache"),
    
    # 上传文件目录
    "uploads": os.path.join(BASE_DIR, "uploads"),
 
}

# 配置文件地址 - 修复逗号导致的元组问题
CONFIG_PATH = os.path.join("SmartPaper/config_files/config.yaml")

# 确保所有缓存目录存在
for dir_name, dir_path in CACHE_DIRS.items():
    os.makedirs(dir_path, exist_ok=True)
    logger.debug(f"确保缓存目录存在: {dir_name} = {dir_path}")

def get_pdf_cache_dir() -> str:
    """获取PDF解析结果缓存目录"""
    return CACHE_DIRS["pdf_cache"]

def get_images_cache_dir() -> str:
    """获取图片缓存目录"""
    return CACHE_DIRS["images_cache"]

def get_uploads_dir() -> str:
    """获取上传文件目录"""
    return CACHE_DIRS["uploads"]

def get_config_path() -> str:
    """获取配置文件路径"""
    return CONFIG_PATH

