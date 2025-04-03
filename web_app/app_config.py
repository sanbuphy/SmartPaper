"""
SmartPaper Web 应用配置模块

该模块包含应用的各种配置选项，包括日志设置、环境初始化和示例数据。
将配置相关的功能集中在此模块可以使主程序更加清晰，并便于维护。
"""

import os  # 用于文件和目录操作
import sys  # 用于系统相关操作，如标准输出
from loguru import logger  # 用于高级日志记录


def setup_logging() -> None:
    """
    配置日志记录系统

    设置loguru记录器，包括日志格式、级别和输出目标。
    将日志输出到标准输出，并设置合适的格式和颜色。

    Returns:
        None: 该函数无返回值
    """
    logger.remove()  # 移除默认处理器
    # 只输出到控制台，不记录到文件
    logger.add(
        sys.stdout,
        level="INFO",  # 设置日志级别为INFO
        format="{time:HH:mm:ss} | <level>{level: <8}</level> | {message}",  # 自定义日志格式
        colorize=True,  # 启用彩色输出
    )


def setup_environment() -> None:
    """
    设置应用运行环境

    创建必要的目录结构，初始化环境变量，以及执行其他启动前的准备工作。

    Returns:
        None: 该函数无返回值
    """
    logger.info("=== SmartPaperGUI启动 ===")
    # 创建输出目录（如果不存在）
    os.makedirs("outputs", exist_ok=True)


def get_example_urls() -> list:
    """
    获取示例论文URL列表

    提供一组预先定义的arXiv论文URL，作为用户可以直接使用的示例。
    包含不同格式（pdf和abs）的arXiv链接，展示系统的自动转换能力。

    Returns:
        list: 含有示例arXiv论文URL的列表
    """
    return [
        "https://arxiv.org/pdf/2303.08774",
        "https://arxiv.org/pdf/2305.12002", 
        "https://arxiv.org/abs/2310.06825", 
        "https://arxiv.org/abs/2307.09288",
        "https://arxiv.org/pdf/2312.11805",
    ]
