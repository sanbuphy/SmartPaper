import re
import os
import traceback
from typing import Optional

import diskcache

def find_and_replace_image_in_stream(
    chunk: str,
    img_ref_buffer: str, 
    collecting_img_ref: bool, 
    image_cache_dir: Optional[str] ,
) -> tuple:
    """
    在流式输出的块中查找并替换图片引用为base64编码的图片
    
    Args:
        chunk: 当前接收到的内容块
        img_ref_buffer: 当前已收集的图片引用缓冲区
        collecting_img_ref: 是否正在收集图片引用
        image_cache_dir: 图片缓存目录
        pdf_name: PDF文件名，用于查询图片
    
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
                    try:
                        # 从img_ref_buffer中提取图片信息
                        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', img_ref_buffer)
                        if img_match:
                            alt_text = img_match.group(1).strip()
                            img_path = img_match.group(2).strip()
                            # 提取文件名作为key
                            key = os.path.splitext(os.path.basename(img_path))[0]
                            
                            # 获取图片缓存实例
                            cache_dir = image_cache_dir
                            image_store = diskcache.Cache(cache_dir)
                            
                            # 尝试获取图片的base64数据
                            base64_data = image_store.get(key)
                            
                            if base64_data:
                                # 创建base64图片引用
                                mime_type = "image/jpeg"  # 默认图片格式
                                processed_text += f'<br><img src="{base64_data}" style="max-width: 50%; display: block; margin-left: auto; margin-right: auto;"><br>'
                            else:
                                # 没有找到对应的图片数据，保留原引用
                                processed_text += img_ref_buffer
                        else:
                            # 正则匹配失败，保留原引用
                            processed_text += img_ref_buffer
                    except Exception as e:
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

