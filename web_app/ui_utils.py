"""
UI 工具和自定义样式

该模块包含与用户界面相关的工具函数和样式定义，
用于美化应用界面、提供一致的用户体验，以及封装常用的UI元素。
"""

import streamlit as st  # Web界面库


def setup_page_config() -> None:
    """
    设置Streamlit页面配置
    
    配置应用的基本外观和行为，包括标题、图标、布局和侧边栏状态。
    应在应用启动时最先调用，以确保正确设置页面。
    
    Returns:
        None: 该函数无返回值
    """
    st.set_page_config(
        page_title="SmartPaper",  # 浏览器标签页标题
        page_icon="📄",  # 标签页图标
        layout="wide",  # 使用宽屏布局
        initial_sidebar_state="expanded"  # 侧边栏默认展开
    )


def apply_custom_css() -> None:
    """
    应用自定义CSS样式
    
    使用HTML/CSS定义应用的视觉样式，使界面更加美观。
    包括颜色、字体、边框、阴影和动画效果等样式定义。
    
    Returns:
        None: 该函数无返回值
    """
    st.markdown(
        """
    <style>
        /* 整体页面样式 - 设置背景色和内边距 */
        .main {
            background-color: #f8f9fa;
            padding: 20px;
        }

        /* 标题样式 - 定义颜色、字重和底部边框 */
        h1 {
            color: #1e3a8a;
            font-weight: 700;
            margin-bottom: 30px;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 2px solid #3b82f6;
        }

        /* 副标题样式 - 左侧添加彩色边框 */
        h3 {
            color: #1e40af;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid #3b82f6;
        }

        /* 聊天消息容器 - 添加圆角和阴影效果 */
        .stChatMessage {
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        /* 按钮样式 - 设置圆角和悬停动画效果 */
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        /* 按钮悬停效果 - 微小上浮和阴影增强 */
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* 下载按钮样式 - 紫色背景白色文字 */
        .stDownloadButton>button {
            background-color: #4f46e5;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 6px;
        }

        /* 侧边栏样式 - 浅灰色背景 */
        .css-1d391kg {
            background-color: #f1f5f9;
            padding: 20px 10px;
        }

        /* 输入框样式 - 圆角和边框 */
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 1px solid #d1d5db;
            padding: 10px;
        }

        /* URL输入框高亮样式 - 突出显示重要输入框 */
        .url-input {
            border: 2px solid #3b82f6 !important;
            background-color: #eff6ff !important;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important;
        }

        /* 选择框样式 - 圆角 */
        .stSelectbox>div>div {
            border-radius: 8px;
        }
    </style>
    """,
        unsafe_allow_html=True,  # 允许HTML渲染
    )


def add_url_highlight_script() -> None:
    """
    添加高亮URL输入框的JavaScript
    
    使用JavaScript动态修改URL输入框样式，使其更加突出显示。
    脚本在页面加载后执行，查找特定输入框并添加自定义CSS类。
    
    Returns:
        None: 该函数无返回值
    """
    st.markdown(
        """
    <script>
        // 等待页面加载完成后执行
        setTimeout(function() {
            // 获取URL输入框并添加高亮样式
            const urlInput = document.querySelector('[data-testid="stTextInput"] input');
            if (urlInput) {
                urlInput.classList.add('url-input');
            }
        }, 500);  // 延迟500毫秒执行，确保DOM已加载
    </script>
    """,
        unsafe_allow_html=True,  # 允许执行JavaScript
    )


def render_header() -> None:
    """
    渲染应用头部
    
    创建应用标题和简短描述，包含项目链接和简介。
    提供统一的应用顶部视觉元素。
    
    Returns:
        None: 该函数无返回值
    """
    # 显示主标题
    st.title("SmartPaper")
    # 显示项目简介和链接
    st.markdown(
        """
    <div style="color: gray; font-size: 0.8em;">
        <b>SmartPaper</b>: <a href="https://github.com/sanbuphy/SmartPaper">GitHub</a> -
        一个迷你助手，帮助您快速阅读论文
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_usage_instructions() -> None:
    """
    渲染使用说明
    
    创建一个美观的使用说明卡片，向用户展示如何使用应用的基本步骤。
    使用蓝色背景和左侧边框设计，突出显示重要信息。
    
    Returns:
        None: 该函数无返回值
    """
    st.markdown(
        """
    <div style="margin-top: 30px; padding: 15px; background-color: #e0f2fe; border-radius: 8px; border-left: 4px solid #0ea5e9;">
        <h4 style="margin-top: 0; color: #0369a1;">使用说明</h4>
        <p style="font-size: 0.9em; color: #0c4a6e;">
            1. 输入arXiv论文URL<br>
            2. 选择合适的提示词模板<br>
            3. 点击"开始分析"按钮<br>
            4. 等待分析完成后可下载结果
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
