import os
import pdfplumber
import io
import base64
import json
from pathlib import Path
import re
import asyncio
import concurrent.futures
import time
from datetime import datetime
from PIL import Image
import uuid  # 添加UUID模块导入

from src.tools.everything_to_text.image_to_text import describe_image, get_image_title


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不合法字符
    
    Args:
        filename (str): 需要清理的原始文件名
    
    Returns:
        str: 清理后的文件名，所有不合法字符(\ / * ? : " < > |)已被替换为下划线
    """
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def extract_text(pdf_path: str, output_dir: str = None) -> dict:
    """
    从PDF文件中提取文本，直接生成Markdown格式内容
    
    Args:
        pdf_path (str): PDF文件路径
        output_dir (str, optional): 输出目录，如果不指定则使用当前目录
    
    Returns:
        dict: 包含以下键的字典：
            - text_content (str): Markdown格式的文本内容
            - metadata (dict): 包含标题等元数据
            - images (list): 提取的图片信息列表
    """
    if output_dir is None:
        output_dir = os.getcwd()
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取PDF文件名（不含扩展名）
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    title = pdf_name  # 使用文件名作为标题
    
    # 图片存储目录
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # 用于存储图片信息的字典
    image_dict = {}
    # 用于返回的图片信息列表
    image_list = []
    
    md_content = f"# {title}\n\n"
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            md_content += f"## 第{page_num + 1}页\n\n"
            
            # 提取文本
            text = page.extract_text() or ""
            md_content += f"{text}\n\n"
            
            # 提取图片
            for img_index, image_obj in enumerate(page.images):
                try:
                    # 生成唯一的UUID标识符
                    img_uuid = str(uuid.uuid4())[:8]  # 使用UUID前8位作为唯一标识
                    
                    # 生成图片文件名和键名，加入UUID确保唯一性
                    image_key = f"page{page_num + 1}_img{img_index + 1}_{img_uuid}"
                    image_filename = f"{image_key}.png"
                    image_path = os.path.join(images_dir, image_filename)
                    
                    # 保存图像
                    im = Image.open(io.BytesIO(image_obj["stream"].get_data()))
                    im.save(image_path)
                    
                    # 转换为base64
                    with open(image_path, "rb") as img_file:
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    
                    # 存储图片信息
                    image_dict[image_key] = img_data
                    image_list.append({
                        "key": image_key,
                        "path": image_path,
                        "filename": image_filename
                    })
                    
                    # 在Markdown中添加图片引用，这里使用image_key作为图片标识符
                    md_content += f"![{image_key}]({image_filename})\n\n"
                    
                except Exception as e:
                    print(f"提取图片时出错: {e}")
            
            md_content += "---\n\n"
    
    # 将图片的base64数据保存到JSON文件
    json_path = os.path.join(output_dir, f"{pdf_name}_images.json")
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(image_dict, json_file)
    
    print(f"处理完成，共提取了 {len(image_list)} 张图片")
    
    return {
        "text_content": md_content,
        "metadata": {"title": title},
        "images": image_list
    }

async def process_image_description_and_title(image_path: str, index: int = None, total: int = None, api_key: str = None) -> dict:
    """
    串行处理图片描述和标题生成 - 将两个必须串行的步骤合并为一个函数
    
    Args:
        image_path (str): 图片文件路径
        index (int, optional): 当前图片的索引，用于日志显示
        total (int, optional): 总图片数量，用于日志显示
        api_key (str, optional): API密钥，用于图像处理API调用。如果不提供，将尝试从环境变量读取。
    
    Returns:
        dict: 包含图片处理结果的字典，具有以下键值对:
            - 'description' (str): 图片的AI生成描述文本
            - 'title' (str): 基于描述生成的图片标题
            - 'desc_time' (float): 生成描述所花费的时间(秒)
            - 'title_time' (float): 生成标题所花费的时间(秒)
    """
    index_info = f"[{index}/{total}]" if index is not None and total is not None else ""
    
    # 第一步：获取图片描述
    start_time = time.time()
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        description = await loop.run_in_executor(pool, describe_image, image_path, "Qwen/Qwen2.5-VL-72B-Instruct", None, api_key)
    desc_time = time.time() - start_time
    print(f"{index_info} 🖼️ 获取图片描述耗时: {desc_time:.2f}秒 - {os.path.basename(image_path)} - 内容: {description[:50]}{'...' if len(description) > 50 else ''}")
    
    # 第二步：基于描述生成标题
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        title = await loop.run_in_executor(pool, get_image_title, description, api_key)
        if not title:
            title = f"图片{os.path.basename(image_path)}"
    title_time = time.time() - start_time
    print(f"{index_info} 📌 生成图片标题耗时: {title_time:.2f}秒 - 标题: {title}")
    
    return {
        'description': description,
        'title': title,
        'desc_time': desc_time,
        'title_time': title_time
    }

async def process_image_async(img_path: str, output_dir: str, index: int = None, total: int = None, api_key: str = None) -> dict:
    """
    异步处理单张图片，获取标题和描述
    
    Args:
        img_path (str): 图片文件的完整路径
        output_dir (str): 输出目录，用于计算相对路径
        index (int, optional): 当前处理的图片索引
        total (int, optional): 总图片数量
        api_key (str, optional): API密钥，用于图像处理API调用
    
    Returns:
        dict: 包含图片处理结果的字典，具有以下键值对:
            - 'path' (str): 图片的绝对路径
            - 'rel_path' (str): 图片相对于输出目录的相对路径，用于Markdown引用
            - 'title' (str): 图片的AI生成标题
            - 'desc' (str): 图片的AI生成描述文本
    """
    index_str = f"[{index}/{total}]" if index is not None else ""
    print(f"{index_str} 开始处理图片: {os.path.basename(img_path)}")
    total_start_time = time.time()
    
    rel_img_path = os.path.relpath(img_path, output_dir)
    
    # 串行处理图片描述和标题生成
    result = await process_image_description_and_title(img_path, index, total, api_key)
    
    total_end_time = time.time()
    print(f"{index_str} ✅ 图片处理完成: {os.path.basename(img_path)} - 总耗时: {total_end_time - total_start_time:.2f}秒\n")
    
    return {
        'path': img_path,
        'rel_path': rel_img_path,
        'title': result['title'],
        'desc': result['description']
    }

async def generate_markdown_report_async(text_content_dict: dict, image_paths: list, output_dir: str, api_key: str = None) -> str:
    """
    异步生成包含文本和图片的Markdown报告
    
    Args:
        text_content_dict (dict): 包含文本内容的字典，格式为extract_text函数返回的格式
            - text_content (str): Markdown格式的文本内容
            - metadata (dict): 包含标题等元数据
            - images (list): 提取的图片信息列表
        image_paths (list[str]): 提取的图片路径列表
        output_dir (str): 输出目录路径
        api_key (str, optional): API密钥，用于图像处理API调用
    
    Returns:
        str: 生成的Markdown报告文件的完整路径。
    """
    # 从text_content_dict中获取标题
    pdf_name = text_content_dict["metadata"]["title"]
    
    # 输出Markdown文件路径
    output_md_path = os.path.join(output_dir, f"{pdf_name}.md")
    
    # 获取已有的Markdown内容
    md_content = text_content_dict["text_content"]
    
    # 一次性处理所有图片
    total_images = len(image_paths)
    print(f"\n开始并发处理所有图片...共 {total_images} 张")
    start_time = time.time()
    
    # 创建带有索引的任务
    tasks = [process_image_async(img_path, output_dir, index+1, total_images, api_key) 
             for index, img_path in enumerate(image_paths)]
    all_processed_images = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / total_images if total_images else 0
    
    # 将处理结果转换为多种映射方式的字典，提高匹配成功率
    image_info_dict = {}
    page_img_pattern = re.compile(r'page(\d+)_img(\d+)')
    
    for img_info in all_processed_images:
        basename = os.path.basename(img_info['path'])
        # 使用完整文件名作为键
        image_info_dict[basename] = img_info
        
        # 尝试提取页码和图片索引信息，创建额外的键
        match = page_img_pattern.search(basename)
        if match:
            page_num = match.group(1)
            img_num = match.group(2)
            # 使用"page{页码}_img{索引}"格式作为额外键
            page_img_key = f"page{page_num}_img{img_num}"
            image_info_dict[page_img_key] = img_info
    
    print(f"\n🎉 所有图片处理完成! 总耗时: {total_time:.2f}秒, 平均每张: {avg_time:.2f}秒")
    
    # 调试信息
    print(f"图片信息字典键值: {list(image_info_dict.keys())}")
    
    # 修改Markdown内容中的图片引用格式
    # 更复杂的正则表达式，可以匹配各种图片引用格式
    img_pattern = r'!\[(.*?)\]\((.*?)\)\s*'
    
    def replace_image_reference(match):
        alt_text = match.group(1)
        img_path = match.group(2)
        img_filename = os.path.basename(img_path)
        
        # 调试信息
        print(f"尝试匹配图片: alt_text={alt_text}, filename={img_filename}")
        
        # 查找对应的图片文件
        matching_info = None
        
        # 1. 尝试直接用文件名匹配
        if img_filename in image_info_dict:
            matching_info = image_info_dict[img_filename]
        # 2. 尝试用alt_text匹配
        elif alt_text in image_info_dict:
            matching_info = image_info_dict[alt_text]
        # 3. 尝试提取alt_text中的页码和图片索引
        else:
            alt_match = page_img_pattern.search(alt_text)
            if alt_match:
                page_img_key = f"page{alt_match.group(1)}_img{alt_match.group(2)}"
                if page_img_key in image_info_dict:
                    matching_info = image_info_dict[page_img_key]
        
        # 找不到匹配，则使用第一个可用的图片信息（备选方案）
        if not matching_info and all_processed_images:
            # 如果找不到匹配，默认使用第一张图片的信息
            print(f"⚠️ 未找到图片 {img_filename} 的匹配信息，使用第一张图片的信息")
            matching_info = all_processed_images[0]
        
        if matching_info:
            img_basename = os.path.basename(matching_info['path'])
            # 使用正确的格式：标题作为alt文本，相对路径，描述作为引用块
            return f"![{matching_info['title']}](./images/{img_basename})\n\n> {matching_info['desc']}\n\n"
        else:
            # 极端情况：如果没有任何匹配且没有任何处理过的图片
            print(f"⚠️ 无法为图片 {img_filename} 找到任何匹配信息")
            return f"![{alt_text}](./images/{img_filename})\n\n"
    
    # 替换所有图片引用
    md_content_p = re.sub(img_pattern, replace_image_reference, md_content)
    
    # 写入增强后的Markdown文件
    with open(output_md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content_p)
    
    # 输出处理完成的信息
    print(f"Markdown报告已生成: {output_md_path}")
    return output_md_path

def extract_images(pdf_path: str, output_dir: str = None) -> list:
    """
    从PDF文件中提取图片
    
    Args:
        pdf_path (str): PDF文件路径
        output_dir (str, optional): 输出目录，如果不指定则使用当前目录
    
    Returns:
        list[str]: 提取的图片文件路径列表，每个元素为一张图片的完整路径。
                   图片保存在output_dir/images/目录下，
                   文件名格式为"page{页码}_img{图片索引}_{uuid}.png"
    """
    if output_dir is None:
        output_dir = os.getcwd()
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取PDF文件名（不含扩展名）
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 创建图片目录
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # 记录提取的图片文件路径
    image_paths = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            for img_index, image_obj in enumerate(page.images):
                try:
                    # 生成唯一的UUID标识符
                    img_uuid = str(uuid.uuid4())[:8]  # 使用UUID前8位作为唯一标识
                    
                    # 生成带有UUID的图片文件名
                    image_filename = f"page{page_num + 1}_img{img_index + 1}_{img_uuid}.png"
                    image_path = os.path.join(images_dir, image_filename)
                    
                    # 保存图像
                    im = Image.open(io.BytesIO(image_obj["stream"].get_data()))
                    im.save(image_path)
                    
                    image_paths.append(image_path)
                except Exception as e:
                    print(f"提取图片时出错: {e}")
    
    if image_paths:
        print(f"共提取了 {len(image_paths)} 张图片")
    return image_paths

async def process_pdf_async(pdf_path: str, output_dir: str = None, api_key: str = None) -> tuple:
    """
    异步处理PDF文件，包括文本提取、图片提取和Markdown报告生成
    
    Args:
        pdf_path (str): 需要处理的PDF文件的完整路径
        output_dir (str, optional): 输出目录路径。如果为None，则创建带时间戳的默认目录
        api_key (str, optional): API密钥，用于图像处理API调用。如果不提供，将尝试从环境变量读取。
    
    Returns:
        tuple[dict, list[str], str]: 包含三个元素的元组:
            - text_content_dict (dict): 包含文本内容的字典
            - image_paths (list[str]): 提取的所有图片路径列表
            - md_path (str): 生成的Markdown报告路径
    """
    # 如果未指定输出目录，则创建带时间戳的默认目录
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 在当前工作目录下创建带时间戳的子目录
        output_dir = os.path.join(os.getcwd(), f"pdf_extract_{timestamp}")
    
    # 确保输出目录存在，如果不存在则创建
    os.makedirs(output_dir, exist_ok=True)
    
    # 输出开始处理的信息，显示PDF文件名
    print(f"开始处理PDF: {os.path.basename(pdf_path)}")
    
    # 获取当前运行中的事件循环，用于执行异步操作
    loop = asyncio.get_running_loop()
    
    # 使用线程池执行提取文本操作
    text_content_dict = await loop.run_in_executor(None, extract_text, pdf_path, output_dir)
    
    # 使用线程池执行提取图片操作
    image_paths = await loop.run_in_executor(None, extract_images, pdf_path, output_dir)
    
    # 异步生成集成了文本和图片的Markdown报告
    md_path = await generate_markdown_report_async(text_content_dict, image_paths, output_dir, api_key)
    
    # 输出处理完成的信息
    print(f"处理完成! 所有文件已保存到: {output_dir}")
    
    # 返回处理结果
    return text_content_dict, image_paths, md_path

def process_pdf(pdf_path: str, output_dir: str = None, api_key: str = None) -> tuple:
    """
    处理PDF文件，提取文本和图片，生成Markdown报告
    (此函数是异步函数process_pdf_async的同步包装器)
    
    Args:
        pdf_path (str): PDF文件的完整路径
        output_dir (str, optional): 输出目录。如果为None，则创建带时间戳的默认目录
        api_key (str, optional): API密钥，用于图像处理API调用。如果不提供，将尝试从环境变量读取。
    
    Returns:
        tuple[dict, list[str], str]: 包含三个元素的元组:
            - text_content_dict (dict): 包含文本内容的字典
            - image_paths (list[str]): 提取的所有图片的路径列表
            - md_path (str): 生成的Markdown报告的完整路径
    """
    return asyncio.run(process_pdf_async(pdf_path, output_dir, api_key)

def pdfplumber_pdf2md(
    file_path: str,
    llm_client: Any = None,
    llm_model: str = None,
    config: Dict = None,
    ocr_enabled: bool = False,
) -> Dict:
    """将PDF文件转换为Markdown，兼容注册转换器接口
    
    这个函数是为了与转换器注册系统兼容而创建的包装函数，
    接口与markitdown_pdf2md保持一致。
    
    Args:
        file_path (str): PDF文件路径
        llm_client (Any, optional): LLM客户端，用于图像描述等高级功能，在本实现中不使用
        llm_model (str, optional): LLM模型名称，在本实现中不使用
        config (Dict, optional): 配置信息，可用于传递api_key
        ocr_enabled (bool, optional): 是否启用OCR功能，在本实现中不使用
    
    Returns:
        Dict: 包含转换结果的字典，格式与process_pdf函数一致
    """
    from typing import Dict, Any, Optional
    
    # 从config中获取api_key，如果有的话
    api_key = None
    if config and 'api_key' in config:
        api_key = config['api_key']
    
    # 确定输出目录
    output_dir = None
    if config and 'output_dir' in config:
        output_dir = config['output_dir']
    
    # 调用实际的处理函数
    text_content_dict, _, md_path = process_pdf(file_path, output_dir, api_key)
    
    # 返回结果
    return text_content_dict

def main() -> None:
    """
    命令行入口函数
    
    解析命令行参数并执行PDF处理流程
    
    Returns:
        None: 此函数无返回值，处理结果将保存到文件系统中
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="使用pdfplumber处理PDF，提取文本和图片，生成Markdown报告")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output", help="输出目录(可选)", default=None)
    parser.add_argument("-k", "--api-key", help="API密钥(可选，默认使用环境变量)", default=None)
    
    args = parser.parse_args()
    process_pdf(args.pdf_path, args.output, args.api_key)

if __name__ == "__main__":
    # main()
    process_pdf("./test_pdf_to_md_pdfplumber.pdf", "./output", None)