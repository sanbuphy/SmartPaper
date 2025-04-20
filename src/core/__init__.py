"""SmartPaper核心功能模块。"""

import os

from pathlib import Path
from loguru import logger


def get_smartpaper_root_path():
    """获取 smartpaper 项目的根目录绝对路径"""
    # 当前文件的绝对路径
    current_path = Path(__file__).resolve()
    # smartpaper 根目录假定为 src 的上一级
    package_root = current_path.parent.parent

    # 检查是否为项目根目录的标志文件
    root_markers = (".git", ".gitignore", "pyproject.toml", "setup.py")

    # 向上查找直到找到项目根目录
    while package_root and not any((package_root / marker).exists() for marker in root_markers):
        old_package_root = package_root
        package_root = package_root.parent
        # 防止无限循环
        if package_root == old_package_root:
            package_root = Path.cwd()
            break

    # 如果找不到根目录标志，使用当前工作目录
    if not any((package_root / marker).exists() for marker in root_markers):
        package_root = Path.cwd()

    # 最终验证
    if not (package_root / "src").exists():
        logger.warning(f"警告：在 {package_root} 未找到 src 目录，可能不是项目根目录")
        # 尝试在当前工作目录查找
        if (Path.cwd() / "src").exists():
            package_root = Path.cwd()
            logger.info(f"已切换到当前工作目录: {package_root}")
        else:
            raise FileNotFoundError(
                f"当前的目录是：{package_root}\n无法找到项目根目录，请确保在正确的目录中运行或重新 `pip install -e .` 安装!"
            )

    logger.info(f"初始化完毕, 当前执行根目录为 {str(package_root)}")
    return package_root


SMART_PATH = get_smartpaper_root_path()

from .document_converter import convert_to_text
from . import register_converters

__all__ = ["convert_to_text", "SMART_PATH"]
