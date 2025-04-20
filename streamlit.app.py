"""
SmartPaper - Streamlit Web界面版本

运行命令:
    streamlit run gui_streamlit_get_prompt_mode_paper.py

功能:
    提供Web界面让用户输入论文URL，选择提示词模板，并实时显示分析结果
"""

import os
import streamlit as st
from loguru import logger
import yaml
import re
from src.core.smart_paper_core import SmartPaper
from src.core.prompt_manager import list_prompts
from typing import List, Dict
import sys
import uuid  # 用于生成用户唯一ID
import traceback  # 用于打印完整的错误栈


def validate_and_format_arxiv_url(url: str) -> str:
    """验证并格式化arXiv URL

    将abs格式转换为pdf格式，并验证URL格式

    Args:
        url: 输入的arXiv URL

    Returns:
        格式化后的URL

    Raises:
        ValueError: 如果URL格式不正确
    """
    logger.debug(f"验证URL格式: {url}")
    # 检查是否是arXiv URL
    arxiv_pattern = r"https?://arxiv\.org/(abs|pdf)/(\d+\.\d+)(v\d+)?"
    match = re.match(arxiv_pattern, url)

    if not match:
        logger.warning(f"URL格式不正确: {url}")
        raise ValueError("URL格式不正确，请提供有效的arXiv URL")

    # 提取arXiv ID
    arxiv_id = match.group(2)
    version = match.group(3) or ""

    # 确保使用PDF格式
    formatted_url = f"https://arxiv.org/pdf/{arxiv_id}{version}"

    if match.group(1) == "abs":
        logger.info(f"URL格式已从abs转换为pdf: {url} -> {formatted_url}")
    else:
        logger.debug(f"URL格式已验证: {formatted_url}")

    return formatted_url


def process_paper(url: str, prompt_name: str = "yuanbao"):
    """处理论文并以流式方式yield结果"""
    try:
        # 验证并格式化URL
        try:
            url = validate_and_format_arxiv_url(url)
        except ValueError as e:
            logger.error(f"URL验证失败: {str(e)}")
            yield {"type": "final", "success": False, "error": str(e)}
            return

        logger.info(f"使用提示词模板: {prompt_name}")
        logger.info(f"处理URL: {url}")

        # 创建输出目录及输出文件，文件名中加入用户 session_id 避免不同用户间冲突
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        session_id = st.session_state.get("session_id", "default")
        output_file = os.path.join(
            output_dir, f'analysis_{session_id}_{url.split("/")[-1]}_prompt_{prompt_name}.md'
        )
        logger.info(f"输出文件将保存至: {output_file}\n")

        # 初始化SmartPaper
        logger.debug("初始化SmartPaper")
        reader = SmartPaper(output_format="markdown")

        # 以写入模式打开文件，覆盖旧内容
        logger.debug(f"开始流式处理论文: {url}")
        with open(output_file, "w", encoding="utf-8") as f:
            chunk_count = 0
            total_length = 0
            for chunk in reader.process_paper_url_stream(url, prompt_name=prompt_name):
                chunk_count += 1
                total_length += len(chunk)
                f.write(chunk)
                if chunk_count % 10 == 0:  # 每10个块记录一次日志，避免日志过多
                    logger.debug(f"已接收 {chunk_count} 个响应块，总长度: {total_length} 字符")
                yield {"type": "chunk", "content": chunk}

        logger.info(f"分析完成，共接收 {chunk_count} 个响应块，总长度: {total_length} 字符")
        logger.info(f"分析结果已保存到: {output_file}")
        yield {"type": "final", "success": True, "file_path": output_file}

    except Exception as e:
        error_msg = f"处理失败: {str(e)}"
        logger.error(error_msg)
        yield {"type": "chunk", "content": f"❌ **错误**: {error_msg}"}
        yield {"type": "final", "success": False, "error": error_msg}


def reanalyze_paper(url: str, prompt_name: str):
    """重新分析指定URL的论文"""
    logger.info(f"重新分析论文: {url}，使用提示词模板: {prompt_name}")
    # 添加用户请求消息到聊天历史
    st.session_state.messages.append(
        {"role": "user", "content": f"请重新分析论文: {url} 使用提示词模板: {prompt_name}"}
    )

    # 创建进度显示区域
    progress_placeholder = st.empty()

    # 处理论文
    with st.spinner("正在重新分析论文..."):
        full_output = ""
        for result in process_paper(url, prompt_name):
            if result["type"] == "chunk":
                full_output += result["content"]
                # 实时更新进度显示
                progress_placeholder.markdown(full_output)
            elif result["type"] == "final":
                if result["success"]:
                    response = full_output
                    file_path = result["file_path"]
                    file_name = os.path.basename(file_path)
                    logger.info(f"重新分析成功，结果保存至: {file_path}")
                    new_message = {
                        "role": "论文分析助手",
                        "content": response,
                        "file_name": file_name,
                        "file_path": file_path,
                        "url": url,  # 保留URL以支持多次重新分析
                    }
                else:
                    logger.error(f"重新分析失败: {result['error']}")
                    response = result["error"]
                    new_message = {
                        "role": "论文分析助手",
                        "content": response,
                        "url": url,  # 即使失败也保留URL
                    }
                st.session_state.messages.append(new_message)
                break

    # 清空进度显示区域
    progress_placeholder.empty()

    # 刷新页面以更新聊天历史
    logger.debug("重新加载页面以更新聊天历史")
    st.rerun()


def main():
    """主函数"""
    logger.info("启动SmartPaperGUI界面")

    # 添加自定义CSS样式
    st.markdown(
        """
    <style>
        /* 整体页面样式 */
        .main {
            background-color: #f8f9fa;
            padding: 20px;
        }

        /* 标题样式 */
        h1 {
            color: #1e3a8a;
            font-weight: 700;
            margin-bottom: 30px;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 2px solid #3b82f6;
        }

        /* 副标题样式 */
        h3 {
            color: #1e40af;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid #3b82f6;
        }

        /* 聊天消息容器 */
        .stChatMessage {
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        /* 按钮样式 */
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* 下载按钮样式 */
        .stDownloadButton>button {
            background-color: #4f46e5;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 6px;
        }

        /* 侧边栏样式 */
        .css-1d391kg {
            background-color: #f1f5f9;
            padding: 20px 10px;
        }

        /* 输入框样式 */
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 1px solid #d1d5db;
            padding: 10px;
        }

        /* URL输入框高亮样式 */
        .url-input {
            border: 2px solid #3b82f6 !important;
            background-color: #eff6ff !important;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important;
        }

        /* 选择框样式 */
        .stSelectbox>div>div {
            border-radius: 8px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # 设置页面标题
    st.title("SmartPaper")
    st.markdown(
        """
    <div style="color: gray; font-size: 0.8em;">
        <b>SmartPaper</b>: <a href="https://github.com/sanbuphy/SmartPaper">GitHub</a> -
        一个迷你助手，帮助您快速阅读论文
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 初始化会话状态
    if "messages" not in st.session_state:
        logger.debug("初始化会话状态: messages")
        st.session_state.messages = []
    if "processed_papers" not in st.session_state:
        logger.debug("初始化会话状态: processed_papers")
        st.session_state.processed_papers = {}
    # 为每个用户生成唯一session_id，防止不同用户文件输出冲突
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex

    # 侧边栏配置
    with st.sidebar:
        st.header("配置选项")

        # 显示可用的提示词模板
        prompt_options = list_prompts()
        logger.debug(f"加载提示词模板，共 {len(prompt_options)} 个")
        selected_prompt = st.selectbox(
            "选择提示词模板",
            options=list(prompt_options.keys()),
            format_func=lambda x: f"{x}: {prompt_options[x]}",
            help="选择用于分析的提示词模板",
        )
        logger.debug(f"用户选择提示词模板: {selected_prompt}")

        # 示例URL列表
        example_urls = [
            "https://arxiv.org/pdf/2305.12002",
            "https://arxiv.org/abs/2310.06825",
            "https://arxiv.org/pdf/2303.08774",
            "https://arxiv.org/abs/2307.09288",
            "https://arxiv.org/pdf/2312.11805",
        ]

        # 创建示例URL选择器
        st.subheader("选择示例论文")
        selected_example = st.selectbox(
            "选择一个示例论文URL",
            options=example_urls,
            format_func=lambda x: x.split("/")[-1] if "/" in x else x,
            help="选择一个预设的论文URL作为示例",
        )

        # 输入论文URL，使用高亮样式
        st.markdown(
            """
        <div style="margin-top: 20px; margin-bottom: 10px; font-weight: bold; color: #1e40af;">
            👇 请在下方输入论文URL 👇
        </div>
        """,
            unsafe_allow_html=True,
        )

        paper_url = st.text_input(
            "论文URL",
            value=selected_example,
            help="输入要分析的论文URL (支持arXiv URL，自动转换为PDF格式)",
            key="paper_url_input",
        )

        # 添加JavaScript来高亮URL输入框
        st.markdown(
            """
        <script>
            // 等待页面加载完成
            setTimeout(function() {
                // 获取URL输入框并添加高亮样式
                const urlInput = document.querySelector('[data-testid="stTextInput"] input');
                if (urlInput) {
                    urlInput.classList.add('url-input');
                }
            }, 500);
        </script>
        """,
            unsafe_allow_html=True,
        )

        if paper_url != selected_example:
            logger.debug(f"用户输入论文URL: {paper_url}")

        # 创建两列布局来放置按钮
        col1, col2 = st.columns(2)
        with col1:
            process_button = st.button("开始分析", use_container_width=True)
        with col2:
            clear_button = st.button("清空结果", use_container_width=True)

        # 添加一些说明信息
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

    # 清空聊天历史和已处理论文记录
    if clear_button:
        logger.info("用户清空分析结果")
        st.session_state.messages = []
        st.session_state.processed_papers = {}

    # 显示聊天历史
    st.write("### 分析结果")
    chat_container = st.container()

    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # 为已处理的论文显示下载按钮
                if "file_name" in message:
                    st.download_button(
                        label=f"下载 {message['file_name']}",
                        data=message["content"],
                        file_name=message["file_name"],
                        mime="text/markdown",
                        key=f"download_{message['file_name']}_{i}",
                    )
                # 添加重新分析功能
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

    # 创建当前分析进展区域
    progress_container = st.container()

    # 处理新论文并流式输出
    if process_button:
        logger.info(f"用户点击开始分析按钮，URL: {paper_url}, 提示词模板: {selected_prompt}")

        # 先验证URL格式，如不正确则直接报错提示并更新会话消息
        try:
            validated_url = validate_and_format_arxiv_url(paper_url)
        except ValueError as exc:
            error_stack = traceback.format_exc()
            logger.error(f"用户输入无效 arXiv URL\n{error_stack}")
            st.error(str(exc))
            st.session_state.messages.append(
                {
                    "role": "论文分析助手",
                    "content": f"错误: {exc}\n\n详细错误信息:\n{error_stack}",
                    "url": paper_url,
                }
            )
            st.experimental_rerun()
            return

        if paper_url in st.session_state.processed_papers:
            logger.warning(f"论文已分析过: {paper_url}")
            st.warning('该论文已经分析过，如果不满意，可以点击对应分析结果的"重新分析"按钮。')
        else:
            # 添加用户消息到聊天历史
            st.session_state.messages.append(
                {"role": "user", "content": f"请分析论文: {paper_url}"}
            )

            # 在进度容器中创建进度显示区域
            with progress_container:
                st.write("### 当前分析进展\n")
                progress_placeholder = st.empty()

            with st.spinner("正在处理论文..."):
                logger.info(f"开始分析论文: {paper_url}")
                full_output = ""
                for result in process_paper(paper_url, selected_prompt):
                    if result["type"] == "chunk":
                        full_output += result["content"]
                        # 实时更新进度显示
                        progress_placeholder.markdown(full_output)
                    elif result["type"] == "final":
                        if result["success"]:
                            logger.info("论文分析成功")
                            response = full_output
                            file_path = result["file_path"]
                            file_name = os.path.basename(file_path)
                            st.session_state.processed_papers[paper_url] = {
                                "content": response,
                                "file_path": file_path,
                                "file_name": file_name,
                            }
                            message = {
                                "role": "论文分析助手",
                                "content": response,
                                "file_name": file_name,
                                "file_path": file_path,
                                "url": paper_url,  # 保留URL以支持多次重新分析
                            }
                            st.session_state.messages.append(message)
                        else:
                            logger.error(f"论文分析失败: {result['error']}")
                            response = result["error"]
                            message = {
                                "role": "论文分析助手",
                                "content": response,
                                "url": paper_url,  # 即使失败也保留URL
                            }
                            st.session_state.messages.append(message)
                        break

            # 分析完成后清空进度显示
            progress_placeholder.empty()

            # 更新聊天历史显示
            with chat_container:
                for i, message in enumerate(st.session_state.messages):
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
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


if __name__ == "__main__":
    # 配置日志记录
    logger.remove()  # 移除默认处理器
    # 只输出到控制台，不记录到文件
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | <level>{level: <8}</level> | {message}",
        colorize=True,
    )

    logger.info("=== SmartPaperGUI启动 ===")

    # 创建必要的目录
    os.makedirs("outputs", exist_ok=True)

    # 配置Streamlit页面
    st.set_page_config(
        page_title="SmartPaper", page_icon="📄", layout="wide", initial_sidebar_state="expanded"
    )

    # 运行主函数
    main()
