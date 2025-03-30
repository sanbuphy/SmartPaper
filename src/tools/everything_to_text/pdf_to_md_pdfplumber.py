import os
import pdfplumber
import io
from pathlib import Path
import re
import asyncio
import concurrent.futures
import time
from datetime import datetime
from PIL import Image

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

def extract_text(pdf_path: str, output_dir: str = None) -> str:
    """
    从PDF文件中提取文本
    
    Args:
        pdf_path (str): PDF文件路径
        output_dir (str, optional): 输出目录，如果不指定则使用当前目录
    
    Returns:
        str: 输出文本文件的完整路径，格式为"{pdf文件名}_text.txt"，用于后续处理或查看
    """
    if output_dir is None:
        output_dir = os.getcwd()
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取PDF文件名（不含扩展名）
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 输出文本文件路径
    output_text_path = os.path.join(output_dir, f"{pdf_name}_text.txt")
    
    # 提取文本
    with pdfplumber.open(pdf_path) as pdf:
        with open(output_text_path, 'w', encoding='utf-8') as text_file:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                text_file.write(f"--- Page {page_num + 1} ---\n")
                text_file.write(text)
                text_file.write("\n\n")
    
    print(f"文本已提取到: {output_text_path}")
    return output_text_path

def extract_images(pdf_path: str, output_dir: str = None) -> list:
    """
    从PDF文件中提取图片
    
    Args:
        pdf_path (str): PDF文件路径
        output_dir (str, optional): 输出目录，如果不指定则使用当前目录
    
    Returns:
        list[str]: 提取的图片文件路径列表，每个元素为一张图片的完整路径。
                   图片保存在output_dir/images/目录下，
                   文件名格式为"page{页码}_img{图片索引}.png"
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
                    # 生成图片文件名
                    image_filename = f"page{page_num + 1}_img{img_index + 1}.png"
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

async def generate_markdown_report_async(text_path: str, image_paths: list, output_dir: str, api_key: str = None) -> str:
    """
    异步生成包含文本和图片的Markdown报告
    
    Args:
        text_path (str): 提取的文本文件路径
        image_paths (list[str]): 提取的图片路径列表
        output_dir (str): 输出目录路径
        api_key (str, optional): API密钥，用于图像处理API调用
    
    Returns:
        str: 生成的Markdown报告文件的完整路径。
             此文件包含了按页组织的PDF内容，每页包括:
             - 页码标题
             - 该页面的图片(如果有)及其描述
             - 该页面的文本内容
    """
    # 获取PDF文件名（不含扩展名）
    pdf_name = os.path.basename(text_path).replace("_text.txt", "")
    
    # 输出Markdown文件路径
    output_md_path = os.path.join(output_dir, f"{pdf_name}.md")
    
    # 读取提取的文本
    with open(text_path, 'r', encoding='utf-8') as text_file:
        all_text = text_file.read()
    
    # 按页分割文本
    pages = all_text.split("--- Page ")
    pages = [page for page in pages if page.strip()]  # 移除空页
    
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
    
    # 将处理结果转换为字典，以便于查找
    image_info_dict = {os.path.basename(img_info['path']): img_info for img_info in all_processed_images}
    
    print(f"\n🎉 所有图片处理完成! 总耗时: {total_time:.2f}秒, 平均每张: {avg_time:.2f}秒")
    
    with open(output_md_path, 'w', encoding='utf-8') as md_file:
        # 遍历每一页，按页码组织内容
        for i, page_content in enumerate(pages):
            page_num = i + 1
            md_file.write(f"## 第{page_num}页\n\n")
            md_file.write("---\n\n")
            
            # 根据页码筛选当前页面的图片
            # page_images: list[str] - 存储当前页的图片路径列表
            # 筛选条件: 文件名中包含"page{页码}_"的图片
            page_images = [img for img in image_paths if f"page{page_num}_" in img]
            
            # 处理当前页面的图片并添加到Markdown文档
            if page_images:
                for img_path in page_images:
                    # img_basename: str - 获取图片的文件名(不含路径)
                    img_basename = os.path.basename(img_path)
                    
                    # 检查图片是否已被成功处理并有对应的信息
                    if img_basename in image_info_dict:
                        # img_info: dict - 包含图片的路径、标题和描述信息
                        img_info = image_info_dict[img_basename]
                        
                        # 以Markdown格式添加图片
                        # ![图片标题](图片相对路径) - Markdown图片语法
                        md_file.write(f"![{img_info['title']}]({img_info['rel_path']})\n")
                        
                        # 添加图片标题和描述作为引用块
                        # > 标题：描述 - Markdown引用语法
                        md_file.write(f"> {img_info['title']}：{img_info['desc']}\n\n")
            
            # 处理并添加页面文本内容
            # text: str - 当前页的文本内容(移除页码标记)
            # 如果页面内容包含换行符，则获取第一个换行符后的所有内容(移除页码标记行)
            text = page_content.split("\n", 1)[1] if "\n" in page_content else page_content
            md_file.write(f"{text}\n\n")
            
            # 添加分隔线作为页面结束标记
            md_file.write("---\n\n")
    
    # 输出处理完成的信息
    print(f"Markdown报告已生成: {output_md_path}")
    return output_md_path

async def process_pdf_async(pdf_path: str, output_dir: str = None, api_key: str = None) -> tuple:
    """
    异步处理PDF文件，包括文本提取、图片提取和Markdown报告生成
    
    Args:
        pdf_path (str): 需要处理的PDF文件的完整路径
        output_dir (str, optional): 输出目录路径。如果为None，则创建带时间戳的默认目录
        api_key (str, optional): API密钥，用于图像处理API调用。如果不提供，将尝试从环境变量读取。
    
    Returns:
        tuple[str, list[str], str]: 包含三个元素的元组:
            - text_path (str): 提取的文本文件路径，保存了PDF的纯文本内容
            - image_paths (list[str]): 提取的所有图片路径列表，每个元素为一张图片的完整路径
            - md_path (str): 生成的Markdown报告路径，整合了文本和图片的完整报告
    """
    # 如果未指定输出目录，则创建带时间戳的默认目录
    # timestamp: str - 当前时间的格式化字符串，用于生成唯一目录名
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 在当前工作目录下创建带时间戳的子目录
        output_dir = os.path.join(os.getcwd(), f"pdf_extract_{timestamp}")
    
    # 确保输出目录存在，如果不存在则创建
    os.makedirs(output_dir, exist_ok=True)
    
    # 输出开始处理的信息，显示PDF文件名
    print(f"开始处理PDF: {os.path.basename(pdf_path)}")
    
    # 获取当前运行中的事件循环，用于执行异步操作
    # loop: asyncio.AbstractEventLoop - 当前的事件循环对象
    loop = asyncio.get_running_loop()
    
    # 使用线程池执行提取文本操作(I/O密集型任务)
    # text_path: str - 提取的文本文件保存路径
    text_path = await loop.run_in_executor(None, extract_text, pdf_path, output_dir)
    
    # 使用线程池执行提取图片操作(I/O密集型任务)
    # image_paths: list[str] - 提取的所有图片文件路径列表
    image_paths = await loop.run_in_executor(None, extract_images, pdf_path, output_dir)
    
    # 异步生成集成了文本和图片的Markdown报告
    # md_path: str - 生成的Markdown报告文件路径
    md_path = await generate_markdown_report_async(text_path, image_paths, output_dir, api_key)
    
    # 输出处理完成的信息
    print(f"处理完成! 所有文件已保存到: {output_dir}")
    
    # 返回处理结果的三个路径组成的元组
    return text_path, image_paths, md_path

def process_pdf(pdf_path: str, output_dir: str = None, api_key: str = None) -> tuple:
    """
    处理PDF文件，提取文本和图片，生成Markdown报告
    (此函数是异步函数process_pdf_async的同步包装器)
    
    Args:
        pdf_path (str): PDF文件的完整路径
        output_dir (str, optional): 输出目录。如果为None，则创建带时间戳的默认目录
        api_key (str, optional): API密钥，用于图像处理API调用。如果不提供，将尝试从环境变量读取。
    
    Returns:
        tuple[str, list[str], str]: 包含三个元素的元组:
            - text_path (str): 提取的文本文件的完整路径，文件包含PDF的纯文本内容
            - image_paths (list[str]): 提取的所有图片的路径列表，每个元素为一张图片的完整路径
            - md_path (str): 生成的Markdown报告的完整路径，该报告整合了文本和图片内容
    """
    return asyncio.run(process_pdf_async(pdf_path, output_dir, api_key))

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
    main()
