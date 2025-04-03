"""
图片处理模块

提供处理Markdown中图片引用的功能，将图片引用替换为base64编码的内嵌图片。
"""

import os
import re
import traceback
from loguru import logger
from src.tools.db.image_store import get_image_store

def process_markdown_images(markdown_content: str, output_dir: str, pdf_name: str) -> str:
    """
    处理Markdown内容中的图片引用，将其替换为base64编码的内嵌图片
    
    Args:
        markdown_content (str): 包含图片引用的Markdown内容
        output_dir (str): 输出目录路径，不再用于定位图片数据库，仅用于日志记录
        pdf_name (str): PDF文件名（不含扩展名），用于查询特定PDF的图片
    
    Returns:
        str: 处理后的Markdown内容，其中图片引用已替换为base64编码
    """
    # 如果内容为空，直接返回
    if not markdown_content:
        return markdown_content
        
    # 获取集中式图片数据库实例
    try:
        image_store = get_image_store()
        
        # 获取指定PDF的所有图片的base64数据
        all_images = image_store.get_all_images(pdf_name)
        
        if not all_images:
            logger.warning(f"数据库中没有PDF {pdf_name} 的图片数据")
            return markdown_content
            
        # 正则表达式匹配Markdown图片引用格式，更加宽松的匹配模式
        # 考虑到可能跨行的情况和特殊格式
        img_pattern = r'!\[(.*?)\]\((.*?)\)'
        
        def replace_with_base64(match):
            alt_text = match.group(1)  # 图片替代文本
            img_path = match.group(2)  # 图片路径
            
            # 去除可能存在的空格
            img_path = img_path.strip()
            
            logger.debug(f"处理图片引用: alt={alt_text}, path={img_path}")
            
            # 尝试提取图片键名
            img_filename = os.path.basename(img_path)
            img_key = os.path.splitext(img_filename)[0]
            
            # 删除键名中可能存在的空格
            img_key = img_key.replace(' ', '')
            
            logger.debug(f"提取的图片键: {img_key}")
            
            # 尝试获取base64数据
            if img_key in all_images:
                # 找到了完全匹配的key
                base64_data = all_images[img_key]
                logger.debug(f"找到完全匹配的图片key: {img_key}")
            else:
                # 尝试部分匹配 - 提取page和img部分
                page_img_pattern = re.compile(r'page(\d+)_img(\d+)')
                match = page_img_pattern.search(img_key)
                
                if match:
                    # 构建不同格式的可能键名
                    page_num = match.group(1)
                    img_num = match.group(2)
                    
                    possible_keys = [
                        f"page{page_num}_img{img_num}",  # 标准格式
                        f"page{int(page_num)}_img{int(img_num)}",  # 去掉前导零
                        f"page{page_num.lstrip('0')}_img{img_num.lstrip('0')}"  # 另一种去前导零方式
                    ]
                    
                    # 查找包含这些可能键的完整键
                    for possible_key in possible_keys:
                        matching_keys = [k for k in all_images.keys() if possible_key in k]
                        if matching_keys:
                            # 使用找到的第一个匹配key
                            chosen_key = matching_keys[0]
                            base64_data = all_images[chosen_key]
                            logger.debug(f"找到部分匹配的图片key: {chosen_key}")
                            break
                    else:
                        # 如果没有任何匹配，尝试更简单的匹配方式
                        simpler_key = f"page{page_num.lstrip('0')}_img{img_num.lstrip('0')}"
                        matching_keys = [k for k in all_images.keys() if 
                                         f"page{int(page_num)}" in k and f"img{int(img_num)}" in k]
                        
                        if matching_keys:
                            chosen_key = matching_keys[0]
                            base64_data = all_images[chosen_key]
                            logger.debug(f"找到简化匹配的图片key: {chosen_key}")
                        else:
                            # 没有匹配，使用第一个可用的图片
                            first_key = list(all_images.keys())[0]
                            base64_data = all_images[first_key]
                            logger.warning(f"未找到匹配的图片 {img_key}，使用第一张图片: {first_key}")
                else:
                    # 如果连部分匹配都无法进行，则使用第一个图片
                    first_key = list(all_images.keys())[0]
                    base64_data = all_images[first_key]
                    logger.warning(f"无法解析图片key {img_key}，使用第一张图片: {first_key}")
            
            # 确定图片MIME类型（假设是PNG，实际应该从原文件或数据中检测）
            mime_type = "image/png"
            
            # 创建内嵌的base64图片引用
            return f'![{alt_text}](data:{mime_type};base64,{base64_data})'
        
        # 替换所有图片引用
        processed_content = re.sub(img_pattern, replace_with_base64, markdown_content)
        return processed_content
        
    except Exception as e:
        logger.error(f"处理Markdown图片时出错: {e}")
        logger.error(traceback.format_exc())
        # 出错时返回原内容，确保不会丢失信息
        return markdown_content


def find_and_replace_image_in_stream(chunk: str, img_ref_buffer: str, collecting_img_ref: bool, 
                                    pdf_info: dict) -> tuple:
    """
    在流式输出的块中查找并替换图片引用
    
    Args:
        chunk (str): 当前接收到的内容块
        img_ref_buffer (str): 当前已收集的图片引用缓冲区
        collecting_img_ref (bool): 是否正在收集图片引用
        pdf_info (dict): PDF信息，包含pdf_name用于查询图片
    
    Returns:
        tuple: (处理后的内容, 更新后的img_ref_buffer, 更新后的collecting_img_ref状态)
    """
    processed_text = ""
    i = 0
    
    while i < len(chunk):
        char = chunk[i]
        
        # 检测图片引用开始标记
        if not collecting_img_ref and char == '!':
            # 查看下一个字符，确认是否是图片引用开始
            if i + 1 < len(chunk) and chunk[i + 1] == '[':
                collecting_img_ref = True
                img_ref_buffer = '!'
                i += 1
                continue
        
        # 正在收集图片引用
        if collecting_img_ref:
            img_ref_buffer += char
            
            # 检测图片引用结束
            if char == ')':
                # 使用正则检查是否是完整的图片引用
                if re.match(r'!\[.*?\]\(.*?\)', img_ref_buffer):
                    # 找到完整的图片引用，准备替换为base64
                    if pdf_info and "pdf_name" in pdf_info:
                        try:
                            # 从img_ref_buffer中提取图片信息
                            img_match = re.match(r'!\[(.*?)\]\((.*?)\)', img_ref_buffer)
                            if img_match:
                                alt_text = img_match.group(1).strip()
                                img_path = img_match.group(2).strip()
                                img_filename = os.path.basename(img_path)
                                print("img_filename:", img_filename)
                                img_key = os.path.splitext(img_filename)[0].replace(' ', '')
                                print(f"提取的图片键: {img_key}")
                                logger.debug(f"流式处理找到图片引用: {img_key}")
                                
                                # 获取图片数据库实例
                                image_store = get_image_store()
                                pdf_name = pdf_info["pdf_name"]
                                
                                # 获取所有相关图片数据
                                all_images = image_store.get_all_images(pdf_name)
                                
                                if all_images:
                                    # 尝试直接匹配键名
                                    if img_key in all_images:
                                        base64_data = all_images[img_key]
                                        logger.debug(f"找到完全匹配的图片key: {img_key}")
                                    else:
                                        # 尝试匹配页码和图片号
                                        page_img_pattern = re.compile(r'page(\d+)_img(\d+)')
                                        match = page_img_pattern.search(img_key)
                                        
                                        if match:
                                            page_num = match.group(1)
                                            img_num = match.group(2)
                                            
                                            # 尝试不同格式的键名
                                            possible_keys = [
                                                f"page{page_num}_img{img_num}",
                                                f"page{int(page_num)}_img{int(img_num)}",
                                                f"page{page_num.lstrip('0')}_img{img_num.lstrip('0')}"
                                            ]
                                            
                                            matching_key = None
                                            for key in possible_keys:
                                                matching_keys = [k for k in all_images.keys() if key in k]
                                                if matching_keys:
                                                    matching_key = matching_keys[0]
                                                    break
                                            
                                            if matching_key:
                                                base64_data = all_images[matching_key]
                                                logger.debug(f"找到部分匹配的图片key: {matching_key}")
                                            else:
                                                # 使用第一个可用图片
                                                first_key = list(all_images.keys())[0]
                                                base64_data = all_images[first_key]
                                                logger.warning(f"未找到匹配图片 {img_key}，使用默认图片: {first_key}")
                                        else:
                                            # 无法解析图片键，使用第一个图片
                                            first_key = list(all_images.keys())[0]
                                            base64_data = all_images[first_key]
                                            logger.warning(f"无法解析图片key {img_key}，使用默认图片")
                                    
                                    # 创建base64图片引用
                                    mime_type = "image/png"
                                    processed_text += f'![{alt_text}](data:{mime_type};base64,{base64_data})'
                                else:
                                    # 没有图片数据，保留原引用
                                    logger.warning(f"PDF {pdf_name} 没有图片数据")
                                    processed_text += img_ref_buffer
                            else:
                                # 正则匹配失败，保留原引用
                                processed_text += img_ref_buffer
                        except Exception as e:
                            logger.error(f"流式处理图片引用失败: {e}")
                            processed_text += img_ref_buffer
                    else:
                        # 没有PDF名称信息，保留原引用
                        processed_text += img_ref_buffer
                    
                    # 重置图片引用收集状态
                    collecting_img_ref = False
                    img_ref_buffer = ""
                else:
                    # 可能是伪图片引用或不完整的图片引用，继续收集更多字符
                    pass
            elif len(img_ref_buffer) > 500:  # 设置最大缓冲区大小，防止内存溢出
                # 图片引用过长，可能是错误格式，放弃收集
                processed_text += img_ref_buffer
                collecting_img_ref = False
                img_ref_buffer = ""
        else:
            # 不在收集图片引用状态，直接添加字符到输出
            processed_text += char
        
        i += 1
    
    return processed_text, img_ref_buffer, collecting_img_ref


def load_image_database(pdf_name: str) -> dict:
    """
    加载指定PDF的图片数据库
    
    Args:
        pdf_name (str): PDF文件名（不含扩展名）
    
    Returns:
        dict: 包含键值对的字典，键为图片ID，值为base64编码
    """
    try:
        image_store = get_image_store()
        all_images = image_store.get_all_images(pdf_name)
        logger.info(f"已加载PDF {pdf_name} 的图片数据，共有 {len(all_images)} 张图片")
        return all_images
    except Exception as e:
        logger.error(f"加载图片数据库失败: {e}")
        return {}
