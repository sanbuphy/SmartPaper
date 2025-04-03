"""
流式输出处理模块

提供处理流式输出内容的功能，包括实时图片引用替换。
"""

import os
import re
from typing import Dict, Generator
import streamlit as st
from loguru import logger

from .image_processor import find_and_replace_image_in_stream, load_image_database

def process_paper_stream(
    paper_url: str, 
    selected_prompt: str, 
    progress_placeholder, 
    paper_processor
) -> Dict:
    """
    处理论文的流式输出，实时替换图片引用
    
    Args:
        paper_url (str): 论文URL
        selected_prompt (str): 选择的提示词模板
        progress_placeholder: Streamlit占位符，用于实时更新进度
        paper_processor: 论文处理器函数
    
    Returns:
        Dict: 包含处理结果的字典
    """
    logger.info(f"开始分析论文: {paper_url}")
    
    # 初始化结果
    full_output = ""  # 存储完整输出
    collecting_img_ref = False  # 是否正在收集图片引用
    img_ref_buffer = ""  # 图片引用缓冲区
    processed_chunks = ""  # 已处理的块内容
    pdf_info = {}  # 存储PDF相关信息
    result_info = {"success": False}  # 存储处理结果
    
    # 调用process_paper生成器函数处理论文
    for result in paper_processor(paper_url, selected_prompt):
        if result["type"] == "chunk":
            # 收到内容片段
            chunk = result["content"]  # 当前块内容
            full_output += chunk  # 添加到完整输出
            
            # 检查是否是从缓存加载的结果
            if not pdf_info and "file_info" in result:
                if "file_path" in result["file_info"]:
                    file_path = result["file_info"]["file_path"]
                    file_name = os.path.basename(file_path)
                    pdf_name = os.path.splitext(file_name)[0]
                    output_dir = os.path.dirname(file_path)
                    
                    # 存储PDF信息，后续用于图片处理
                    pdf_info = {
                        "pdf_name": pdf_name,
                        "output_dir": output_dir,
                        "file_path": file_path,
                        "file_name": file_name
                    }
                    logger.info(f"获取到PDF信息: {pdf_name}, {output_dir}")
                    
                    # 加载图片数据
                    all_images = load_image_database(pdf_name)
                    if all_images:
                        pdf_info["all_images"] = all_images
                
                # 检查是否有缓存标记
                if "from_cache" in result["file_info"] and result["file_info"]["from_cache"]:
                    logger.info(f"使用缓存的PDF解析结果: {pdf_name}")
            
            # 处理当前块中的图片引用
            if pdf_info:
                processed_chunk, img_ref_buffer, collecting_img_ref = find_and_replace_image_in_stream(
                    chunk, img_ref_buffer, collecting_img_ref, pdf_info
                )
                processed_chunks += processed_chunk
            else:
                processed_chunks += chunk
            
            # 更新显示，使用处理后的内容
            progress_placeholder.markdown(processed_chunks, unsafe_allow_html=True)
                
        elif result["type"] == "final":
            # 收到最终结果
            result_info = {
                "success": result["success"],
                "full_output": full_output,
                "processed_output": processed_chunks,
            }
            
            if result["success"]:
                result_info["file_path"] = result["file_path"]
                result_info["file_name"] = os.path.basename(result["file_path"]) 
                result_info["pdf_name"] = os.path.splitext(result_info["file_name"])[0]
            else:
                result_info["error"] = result["error"]
                
            break  # 处理完成，退出循环
    
    return result_info
