"""
SmartPaper Web 应用包

该包包含 SmartPaper Web 界面的所有组件，将各个功能模块组织在一起
便于导入和使用。该模块作为web_app包的入口点。
"""

# 从main模块导入主函数，使其可以通过web_app包直接访问
from .main import main

# 指定从该包导入时默认可用的符号
__all__ = ["main"]
