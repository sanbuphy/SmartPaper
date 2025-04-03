"""
SmartPaper Web 应用主模块

该模块包含应用的主要逻辑和UI布局，整合其他模块的功能，
处理用户交互和应用流程。作为web_app包的核心功能入口。
"""

import os  # 文件和目录操作
import uuid  # 用于生成唯一标识符
import streamlit as st  # Web界面库
from loguru import logger  # 日志记录
import traceback  # 异常堆栈跟踪
from src.core.prompt_manager import list_prompts  # 导入提示词模板管理工具

# 从同包中导入其他模块
from .paper_processor import process_paper, reanalyze_paper, validate_and_format_arxiv_url
from .ui_utils import (
    setup_page_config,
    apply_custom_css,
    add_url_highlight_script,
    render_header,
    render_usage_instructions,
)
from .app_config import get_example_urls
from .image_processor import process_markdown_images
from .stream_processor import process_paper_stream


def render_sidebar():
    """渲染应用侧边栏"""
    with st.sidebar:
        st.header("配置选项")

        # 显示可用的提示词模板选择器
        prompt_options = list_prompts()
        logger.debug(f"加载提示词模板，共 {len(prompt_options)} 个")
        selected_prompt = st.selectbox(
            "选择提示词模板",  # 选择器标签
            options=list(prompt_options.keys()),
            format_func=lambda x: f"{x}: {prompt_options[x]}",
            help="选择用于分析的提示词模板",
        )
        logger.debug(f"用户选择提示词模板: {selected_prompt}")

        # 获取示例URL列表
        example_urls = get_example_urls()

        # 创建示例URL选择器
        st.subheader("选择示例论文")
        selected_example = st.selectbox(
            "选择一个示例论文URL",
            options=example_urls,
            format_func=lambda x: x.split("/")[-1] if "/" in x else x,
            help="选择一个预设的论文URL作为示例",
        )

        # 输入论文URL区域标题，使用高亮样式
        st.markdown(
            """
        <div style="margin-top: 20px; margin-bottom: 10px; font-weight: bold; color: #1e40af;">
            👇 请在下方输入论文URL 👇
        </div>
        """,
            unsafe_allow_html=True,
        )

        # URL输入框，默认值为选中的示例URL
        paper_url = st.text_input(
            "论文URL",
            value=selected_example,
            help="输入要分析的论文URL (支持arXiv URL，自动转换为PDF格式)",
            key="paper_url_input",
        )

        # 添加JavaScript来高亮URL输入框
        add_url_highlight_script()

        # 如果用户输入了不同于示例的URL，记录日志
        if paper_url != selected_example:
            logger.debug(f"用户输入论文URL: {paper_url}")

        # 创建两列布局来放置按钮
        col1, col2 = st.columns(2)
        with col1:
            # 第一列放置"开始分析"按钮
            process_button = st.button("开始分析", use_container_width=True)
        with col2:
            # 第二列放置"清空结果"按钮
            clear_button = st.button("清空结果", use_container_width=True)

        # 添加使用说明信息
        render_usage_instructions()
        
    return paper_url, selected_prompt, process_button, clear_button


def render_chat_history():
    """渲染聊天历史显示"""
    st.write("### 分析结果")
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)
                
                if "file_name" in message:
                    st.download_button(
                        label=f"下载 {message['file_name']}",
                        data=message["content"],
                        file_name=message["file_name"],
                        mime="text/markdown",
                        key=f"download_{message['file_name']}_{i}",
                    )
                
                if "url" in message:
                    with st.expander("重新分析"):
                        prompt_options = list_prompts()
                        selected_prompt_reanalyze = st.selectbox(
                            "选择提示词模板",
                            options=list(prompt_options.keys()),
                            format_func=lambda x: f"{x}: {prompt_options[x]}",
                            key=f"reanalyze_prompt_{i}",
                        )
                        if st.button("重新分析", key=f"reanalyze_button_{i}"):
                            logger.info(
                                f"用户请求重新分析，使用提示词模板: {selected_prompt_reanalyze}"
                            )
                            reanalyze_paper(message["url"], selected_prompt_reanalyze)
    
    return chat_container


def handle_paper_processing(paper_url, selected_prompt, progress_placeholder):
    """处理论文分析过程并返回结果"""
    with st.spinner("正在处理论文..."):
        # 使用流式处理模块处理论文
        result = process_paper_stream(
            paper_url, selected_prompt, progress_placeholder, process_paper
        )
        
        if result["success"]:
            # 处理成功
            logger.info("论文分析成功" + (" (从缓存加载)" if result.get("from_cache") else ""))
            file_path = result["file_path"]
            file_name = result["file_name"]
            pdf_name = result["pdf_name"]
            
            # 如果是从缓存加载，processed_output已经包含处理过的图片引用
            processed_response = result["processed_output"]
            
            # 将结果存入会话状态
            st.session_state.processed_papers[paper_url] = {
                "content": processed_response,
                "file_path": file_path,
                "file_name": file_name,
            }
            
            # 创建助手响应消息
            return {
                "role": "论文分析助手",
                "content": processed_response,
                "file_name": file_name,
                "file_path": file_path,
                "url": paper_url,
            }
        else:
            # 处理失败
            logger.error(f"论文分析失败: {result.get('error', '未知错误')}")
            # 创建包含错误信息的响应消息
            return {
                "role": "论文分析助手",
                "content": result.get("error", "处理过程中发生未知错误"),
                "url": paper_url,
            }


def initialize_session_state():
    """初始化会话状态变量"""
    if "messages" not in st.session_state:
        logger.debug("初始化会话状态: messages")
        st.session_state.messages = []
    
    if "processed_papers" not in st.session_state:
        logger.debug("初始化会话状态: processed_papers")
        st.session_state.processed_papers = {}
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex


def main() -> None:
    """
    Web应用主函数
    
    组织整个应用的界面布局和交互逻辑，处理用户输入和操作响应。
    这是应用的核心部分，整合了所有功能模块。
    
    Returns:
        None: 该函数无返回值
    """
    logger.info("启动SmartPaperGUI界面")

    # 应用自定义CSS样式
    apply_custom_css()

    # 渲染应用头部
    render_header()

    # 初始化会话状态变量
    initialize_session_state()

    # 渲染侧边栏并获取用户输入
    paper_url, selected_prompt, process_button, clear_button = render_sidebar()

    # 清空聊天历史和已处理论文记录
    if clear_button:
        logger.info("用户清空分析结果")
        st.session_state.messages = []
        st.session_state.processed_papers = {}

    # 渲染聊天历史
    chat_container = render_chat_history()

    # 创建当前分析进展区域
    progress_container = st.container()

    # 处理新论文并流式输出
    if process_button:
        logger.info(f"用户点击开始分析按钮，URL: {paper_url}, 提示词模板: {selected_prompt}")

        # 验证URL格式
        try:
            validated_url = validate_and_format_arxiv_url(paper_url)
        except ValueError as exc:
            error_stack = traceback.format_exc()
            logger.error(f"用户输入无效 arXiv URL\n{error_stack}")
            st.error(str(exc))
            
            st.session_state.messages.append({
                "role": "论文分析助手",
                "content": f"错误: {exc}\n\n详细错误信息:\n{error_stack}",
                "url": paper_url,
            })
            st.experimental_rerun()
            return

        # 检查论文是否已经分析过
        if paper_url in st.session_state.processed_papers:
            logger.warning(f"论文已分析过: {paper_url}")
            st.warning('该论文已经分析过，如果不满意，可以点击对应分析结果的"重新分析"按钮。')
        else:
            # 添加用户消息到聊天历史
            st.session_state.messages.append({
                "role": "user", 
                "content": f"请分析论文: {paper_url}"
            })

            # 在进度容器中创建进度显示区域
            with progress_container:
                st.write("### 当前分析进展\n")
                progress_placeholder = st.empty()

                # 处理论文分析
                message = handle_paper_processing(
                    paper_url, selected_prompt, progress_placeholder
                )
                st.session_state.messages.append(message)

            # 分析完成后清空进度显示
            progress_placeholder.empty()

            # 更新聊天历史显示
            render_chat_history()
