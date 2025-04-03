"""
SmartPaper - Web界面版入口点

该模块是整个应用的启动入口，负责启动Web界面应用。
用户可以通过运行此文件来启动SmartPaper的Web界面。

运行命令:
    python app.py

功能:
    启动SmartPaper的Web界面应用
"""

import os  # 用于路径操作
import sys  # 用于系统路径和环境变量
from loguru import logger  # 用于高级日志记录

# 添加项目根目录到系统路径，确保可以导入项目中的模块
current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件目录的绝对路径
sys.path.insert(0, current_dir)  # 将项目根目录添加到Python模块搜索路径

# 导入web应用相关模块
from web_app.app_config import setup_logging, setup_environment  # 导入配置相关函数
from web_app.ui_utils import setup_page_config  # 导入UI设置相关函数
from web_app.main import main  # 导入应用主函数

if __name__ == "__main__":
    # 配置日志记录系统
    setup_logging()
    
    # 设置应用环境，创建必要的目录
    setup_environment()
    
    # 配置Streamlit页面外观和行为
    setup_page_config()
    
    # 运行主应用函数
    main()
