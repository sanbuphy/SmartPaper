import os
import streamlit as st
from loguru import logger
import yaml
from src.core.processor import PaperProcessor
from src.prompts.prompt_library import list_prompts
from typing import List, Dict

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def process_paper(url: str, prompt_name: str = 'yuanbao'):
    """处理论文并以流式方式yield结果"""
    try:
        logger.info(f"使用提示词模板: {prompt_name}")

        # 创建输出目录及输出文件
        output_dir = 'outputs'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'analysis_{url.split("/")[-1]}_prompt_{prompt_name}.md')

        # 加载配置
        config = load_config()

        # 初始化PaperProcessor
        processor = PaperProcessor(config)

        # 以写入模式打开文件，覆盖旧内容
        with open(output_file, 'w', encoding='utf-8') as f:
            for chunk in processor.process_stream(url, prompt_name=prompt_name):
                f.write(chunk)
                yield {"type": "chunk", "content": chunk}

        logger.info(f"分析结果已保存到: {output_file}")
        yield {"type": "final", "success": True, "file_path": output_file}

    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        yield {"type": "final", "success": False, "error": str(e)}

def reanalyze_paper(url: str, prompt_name: str):
    """重新分析指定URL的论文"""
    # 添加用户请求消息到聊天历史
    st.session_state.messages.append({
        "role": "user",
        "content": f"请重新分析论文: {url} 使用提示词模板: {prompt_name}"
    })
    # 处理论文
    with st.spinner("正在重新分析论文..."):
        full_output = ""
        for result in process_paper(url, prompt_name):
            if result["type"] == "chunk":
                full_output += result["content"]
            elif result["type"] == "final":
                if result["success"]:
                    response = full_output
                    file_path = result["file_path"]
                    file_name = os.path.basename(file_path)
                    new_message = {
                        "role": "论文分析助手",
                        "content": response,
                        "file_name": file_name,
                        "file_path": file_path,
                        "url": url  # 保留URL以支持多次重新分析
                    }
                else:
                    response = result["error"]
                    new_message = {
                        "role": "论文分析助手",
                        "content": response,
                        "url": url  # 即使失败也保留URL
                    }
                st.session_state.messages.append(new_message)
                break
    # 刷新页面以更新聊天历史
    st.rerun()

def main():
    """主函数"""
    # 设置页面标题
    st.title("论文分析工具")

    # 初始化会话状态
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processed_papers" not in st.session_state:
        st.session_state.processed_papers = {}

    # 侧边栏配置
    with st.sidebar:
        st.header("配置选项")

        # 显示可用的提示词模板
        prompt_options = list_prompts()
        selected_prompt = st.selectbox(
            "选择提示词模板",
            options=list(prompt_options.keys()),
            format_func=lambda x: f"{x}: {prompt_options[x]}",
            help="选择用于分析的提示词模板"
        )

        # 输入论文URL
        default_url = 'https://arxiv.org/pdf/2305.12002'
        paper_url = st.text_input(
            "论文URL",
            value=default_url,
            help="输入要分析的论文URL"
        )

        # 创建两列布局来放置按钮
        col1, col2 = st.columns(2)
        with col1:
            process_button = st.button("开始分析")
        with col2:
            clear_button = st.button("清空分析结果")

    # 清空聊天历史和已处理论文记录
    if clear_button:
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
                        key=f"download_{message['file_name']}_{i}"  # 使用索引确保唯一性
                    )
                # 添加重新分析功能
                if "url" in message:
                    with st.expander("重新分析"):
                        prompt_options = list_prompts()
                        selected_prompt_reanalyze = st.selectbox(
                            "选择提示词模板",
                            options=list(prompt_options.keys()),
                            format_func=lambda x: f"{x}: {prompt_options[x]}",
                            key=f"reanalyze_prompt_{i}"  # 唯一键
                        )
                        if st.button("重新分析", key=f"reanalyze_button_{i}"):  # 唯一键
                            reanalyze_paper(message["url"], selected_prompt_reanalyze)

    # 处理新论文并流式输出
    if process_button:
        if paper_url in st.session_state.processed_papers:
            st.warning("该论文已经分析过，如果不满意，可以点击对应分析结果的“重新分析”按钮。")
        else:
            # 添加用户消息到聊天历史
            st.session_state.messages.append({
                "role": "user",
                "content": f"请分析论文: {paper_url}"
            })
            # 显示当前聊天历史
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
                                key=f"download_{message['file_name']}_{i}"
                            )
                        if "url" in message:
                            with st.expander("重新分析"):
                                prompt_options = list_prompts()
                                selected_prompt_reanalyze = st.selectbox(
                                    "选择提示词模板",
                                    options=list(prompt_options.keys()),
                                    format_func=lambda x: f"{x}: {prompt_options[x]}",
                                    key=f"reanalyze_prompt_{i}"
                                )
                                if st.button("重新分析", key=f"reanalyze_button_{i}"):
                                    reanalyze_paper(message["url"], selected_prompt_reanalyze)

            # 创建当前分析进展区域
            st.write("### 当前分析进展")
            progress_placeholder = st.empty()

            with st.spinner("正在处理论文..."):
                full_output = ""
                for result in process_paper(paper_url, selected_prompt):
                    if result["type"] == "chunk":
                        full_output += result["content"]
                        progress_placeholder.markdown(full_output)
                    elif result["type"] == "final":
                        if result["success"]:
                            response = full_output
                            file_path = result["file_path"]
                            file_name = os.path.basename(file_path)
                            st.session_state.processed_papers[paper_url] = {
                                "content": response,
                                "file_path": file_path,
                                "file_name": file_name
                            }
                            message = {
                                "role": "论文分析助手",
                                "content": response,
                                "file_name": file_name,
                                "file_path": file_path,
                                "url": paper_url  # 添加URL以支持重新分析
                            }
                        else:
                            response = result["error"]
                            message = {
                                "role": "论文分析助手",
                                "content": response,
                                "url": paper_url  # 添加URL以支持重新分析
                            }
                        st.session_state.messages.append(message)
                        break

            # 清除进展显示
            progress_placeholder.empty()

            # 刷新页面以更新聊天历史
            st.rerun()

if __name__ == '__main__':
    # 配置Streamlit页面
    st.set_page_config(
        page_title="论文分析工具",
        page_icon="📄",
        layout="wide"
    )
    main()