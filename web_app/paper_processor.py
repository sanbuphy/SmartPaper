"""
论文处理相关功能模块

该模块包含处理论文的核心功能，从URL验证到内容分析再到结果生成。
主要负责论文的获取、处理和分析等操作，是系统的核心处理逻辑部分。
"""

import os  # 文件和目录操作
import re  # 正则表达式
import streamlit as st  # Web界面库
import traceback  # 异常堆栈跟踪
from loguru import logger  # 日志记录
from src.core.smart_paper_core import SmartPaper  # 导入论文处理核心
from web_app.image_processor import find_and_replace_image_in_stream  # 导入图片处理函数


def validate_and_format_arxiv_url(url: str) -> str:
    """
    验证并格式化arXiv URL

    将abs格式转换为pdf格式，并验证URL格式是否符合arXiv规范。
    支持自动转换从摘要页面链接到PDF直接下载链接。

    Args:
        url (str): 输入的arXiv URL，可以是abs格式或pdf格式

    Returns:
        str: 格式化后的URL，始终为PDF格式

    Raises:
        ValueError: 如果URL格式不正确，例如不是有效的arXiv链接
    """
    logger.debug(f"验证URL格式: {url}")
    # 检查是否是arXiv URL，使用正则表达式匹配格式
    arxiv_pattern = r"https?://arxiv\.org/(abs|pdf)/(\d+\.\d+)(v\d+)?"
    match = re.match(arxiv_pattern, url)

    if not match:
        logger.warning(f"URL格式不正确: {url}")
        raise ValueError("URL格式不正确，请提供有效的arXiv URL")

    # 提取arXiv ID和版本信息（如果有）
    arxiv_id = match.group(2)  # 论文ID部分（如2305.12002）
    version = match.group(3) or ""  # 版本号部分（如v1），如果没有则为空字符串

    # 确保使用PDF格式，构造标准格式的PDF链接
    formatted_url = f"https://arxiv.org/pdf/{arxiv_id}{version}"

    # 记录URL格式转换的日志
    if match.group(1) == "abs":
        logger.info(f"URL格式已从abs转换为pdf: {url} -> {formatted_url}")
    else:
        logger.debug(f"URL格式已验证: {formatted_url}")

    return formatted_url


def process_paper(url: str, prompt_name: str = "yuanbao"):
    """
    处理论文并以流式方式yield结果

    核心函数，负责下载和分析论文内容，使用选定的提示词模板生成分析报告。
    使用生成器模式，可以实时返回处理过程中的结果片段，支持流式显示。

    Args:
        url (str): 论文的URL，会自动验证和格式化
        prompt_name (str, optional): 使用的提示词模板名称。默认为"yuanbao"

    Yields:
        dict: 包含处理状态和内容的字典，有两种类型：
            - {"type": "chunk", "content": str}: 处理过程中的内容片段
            - {"type": "final", "success": bool, ...}: 最终结果状态
    """
    try:
        # 验证并格式化URL
        try:
            url = validate_and_format_arxiv_url(url)
        except ValueError as e:
            logger.error(f"URL验证失败: {str(e)}")
            yield {"type": "final", "success": False, "error": str(e)}
            return

        # 从URL中提取PDF名称，用于图片处理
        pdf_name = url.split("/")[-1].replace(".pdf", "")
        logger.info(f"提取的PDF名称: {pdf_name}")

        logger.info(f"使用提示词模板: {prompt_name}")
        logger.info(f"处理URL: {url}")

        # 创建输出目录及输出文件，文件名中加入用户 session_id 避免不同用户间冲突
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        # 从会话状态获取唯一session_id，防止文件名冲突
        session_id = st.session_state.get("session_id", "default")
        # 构建输出文件路径，包含会话ID、论文ID和提示词模板名称
        output_file = os.path.join(
            output_dir,
            f'analysis_{session_id}_{url.split("/")[-1]}_prompt_{prompt_name}.md',
        )
        logger.info(f"输出文件将保存至: {output_file}\n")

        # 初始化SmartPaper处理器
        logger.debug("初始化SmartPaper")
        reader = SmartPaper(output_format="markdown")  # 使用markdown输出格式

        # 为流式图片处理准备变量
        img_ref_buffer = ""  # 图片引用缓冲区
        collecting_img_ref = False  # 是否正在收集图片引用
        pdf_info = {"pdf_name": pdf_name}  # PDF信息

        # 以写入模式打开文件，覆盖旧内容
        logger.debug(f"开始流式处理论文: {url}")
        with open(output_file, "w", encoding="utf-8") as f:
            chunk_count = 0  # 记录接收的响应块数量
            total_length = 0  # 记录总响应长度

            # 流式处理论文，每次接收一个响应块
            for chunk in reader.process_paper_url_stream(
                url, mode="prompt", prompt_name=prompt_name
            ):
                chunk_count += 1
                total_length += len(chunk)

                # 处理内容中的图片引用，替换为base64编码
                processed_chunk, img_ref_buffer, collecting_img_ref = (
                    find_and_replace_image_in_stream(
                        chunk, img_ref_buffer, collecting_img_ref, pdf_info
                    )
                )

                f.write(processed_chunk)  # 写入处理后的内容到文件
                # 每10个块记录一次日志，避免日志过多
                if chunk_count % 10 == 0:
                    logger.debug(
                        f"已接收 {chunk_count} 个响应块，总长度: {total_length} 字符"
                    )

                # 使用yield返回当前块，供前端实时显示
                yield {
                    "type": "chunk",
                    "content": processed_chunk,
                }  # 返回处理后的内容块供前端显示

        # 处理完成，记录统计信息
        logger.info(
            f"分析完成，共接收 {chunk_count} 个响应块，总长度: {total_length} 字符"
        )
        logger.info(f"分析结果已保存到: {output_file}")
        # 返回最终成功状态和文件路径
        yield {"type": "final", "success": True, "file_path": output_file}

    except Exception as e:
        # 捕获处理过程中的所有异常
        error_stack = traceback.format_exc()  # 获取完整错误堆栈
        logger.error(f"处理失败: {str(e)}\n{error_stack}")
        # 返回错误状态和详细信息
        yield {
            "type": "final",
            "success": False,
            "error": f"{str(e)}\n\n详细错误信息:\n{error_stack}",
        }


def reanalyze_paper(url: str, prompt_name: str) -> None:
    """
    重新分析指定URL的论文

    当用户请求重新分析已经处理过的论文时调用此函数，
    可以使用不同的提示词模板重新生成分析结果。

    Args:
        url (str): 要重新分析的论文URL
        prompt_name (str): 重新分析时使用的提示词模板名称

    Returns:
        None: 该函数无返回值，但会更新会话状态并重新加载页面
    """
    logger.info(f"重新分析论文: {url}，使用提示词模板: {prompt_name}")
    # 添加用户请求消息到聊天历史
    st.session_state.messages.append(
        {
            "role": "user",
            "content": f"请重新分析论文: {url} 使用提示词模板: {prompt_name}",
        }
    )

    # 从URL中提取PDF名称，用于图片处理
    pdf_name = url.split("/")[-1].replace(".pdf", "")
    logger.info(f"提取的PDF名称用于图片处理: {pdf_name}")

    # 为流式图片处理准备变量
    img_ref_buffer = ""
    collecting_img_ref = False
    pdf_info = {"pdf_name": pdf_name}

    # 创建进度显示区域
    progress_placeholder = st.empty()

    # 处理论文
    with st.spinner("正在重新分析论文..."):
        full_output = ""  # 存储完整输出内容
        # 调用process_paper处理论文并获取结果
        for result in process_paper(url, prompt_name):
            if result["type"] == "chunk":
                # 内容片段，追加并显示
                full_output += result["content"]
                # 实时更新进度显示
                progress_placeholder.markdown(full_output)
            elif result["type"] == "final":
                # 最终结果状态
                if result["success"]:
                    # 处理成功
                    response = full_output
                    file_path = result["file_path"]
                    file_name = os.path.basename(file_path)
                    logger.info(f"重新分析成功，结果保存至: {file_path}")
                    # 创建包含成功结果信息的消息
                    new_message = {
                        "role": "论文分析助手",
                        "content": response,
                        "file_name": file_name,
                        "file_path": file_path,
                        "url": url,  # 保留URL以支持多次重新分析
                    }
                else:
                    # 处理失败
                    logger.error(f"重新分析失败: {result['error']}")
                    response = result["error"]
                    # 创建包含错误信息的消息
                    new_message = {
                        "role": "论文分析助手",
                        "content": response,
                        "url": url,  # 即使失败也保留URL
                    }
                # 将新消息添加到会话历史中
                st.session_state.messages.append(new_message)
                break

    # 清空进度显示区域
    progress_placeholder.empty()

    # 刷新页面以更新聊天历史
    logger.debug("重新加载页面以更新聊天历史")
    st.rerun()  # 触发Streamlit页面重新运行
