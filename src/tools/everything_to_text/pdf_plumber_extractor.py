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


def sanitize_filename(filename):
    """清理文件名，移除不合法字符"""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def extract_text(pdf_path, output_dir=None):
    """
    从PDF文件中提取文本
    
    Args:
        pdf_path (str): PDF文件路径
        output_dir (str, optional): 输出目录，如果不指定则使用当前目录
    
    Returns:
        str: 输出文件的路径
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

def extract_images(pdf_path, output_dir=None):
    """
    从PDF文件中提取图片
    
    Args:
        pdf_path (str): PDF文件路径
        output_dir (str, optional): 输出目录，如果不指定则使用当前目录
    
    Returns:
        list: 提取的图片文件路径列表
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

async def process_image_description_and_title(image_path, index=None, total=None):
    """
    串行处理图片描述和标题生成 - 将两个必须串行的步骤合并为一个函数
    """
    index_info = f"[{index}/{total}]" if index is not None and total is not None else ""
    
    # 第一步：获取图片描述
    start_time = time.time()
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        description = await loop.run_in_executor(pool, describe_image, image_path)
    desc_time = time.time() - start_time
    print(f"{index_info} 🖼️ 获取图片描述耗时: {desc_time:.2f}秒 - {os.path.basename(image_path)} - 内容: {description[:50]}{'...' if len(description) > 50 else ''}")
    
    # 第二步：基于描述生成标题
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        title = await loop.run_in_executor(pool, get_image_title, description)
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

async def process_image_async(img_path, output_dir, index=None, total=None):
    """
    异步处理单张图片，获取标题和描述
    """
    index_str = f"[{index}/{total}]" if index is not None else ""
    print(f"{index_str} 开始处理图片: {os.path.basename(img_path)}")
    total_start_time = time.time()
    
    rel_img_path = os.path.relpath(img_path, output_dir)
    
    # 串行处理图片描述和标题生成
    result = await process_image_description_and_title(img_path, index, total)
    
    total_end_time = time.time()
    print(f"{index_str} ✅ 图片处理完成: {os.path.basename(img_path)} - 总耗时: {total_end_time - total_start_time:.2f}秒\n")
    
    return {
        'path': img_path,
        'rel_path': rel_img_path,
        'title': result['title'],
        'desc': result['description']
    }

async def generate_markdown_report_async(text_path, image_paths, output_dir):
    """
    异步生成包含文本和图片的Markdown报告
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
    tasks = [process_image_async(img_path, output_dir, index+1, total_images) 
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
            
            # 获取当前页的图片
            page_images = [img for img in image_paths if f"page{page_num}_" in img]
            
            # 处理当前页面的图片
            if page_images:
                for img_path in page_images:
                    img_basename = os.path.basename(img_path)
                    if img_basename in image_info_dict:
                        img_info = image_info_dict[img_basename]
                        # 添加图片和描述到Markdown
                        md_file.write(f"![{img_info['title']}]({img_info['rel_path']})\n")
                        md_file.write(f"> {img_info['title']}：{img_info['desc']}\n\n")
            
            # 添加页面文字（移除页码标记）
            text = page_content.split("\n", 1)[1] if "\n" in page_content else page_content
            md_file.write(f"{text}\n\n")
            
            md_file.write("---\n\n")
    
    print(f"Markdown报告已生成: {output_md_path}")
    return output_md_path

async def process_pdf_async(pdf_path, output_dir=None):
    """
    异步处理PDF文件
    """
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), f"pdf_extract_{timestamp}")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"开始处理PDF: {os.path.basename(pdf_path)}")
    
    # 提取文本和图片 (这些操作是I/O密集型的，但它们在内部已经有自己的循环，不需要额外的异步)
    loop = asyncio.get_running_loop()
    text_path = await loop.run_in_executor(None, extract_text, pdf_path, output_dir)
    image_paths = await loop.run_in_executor(None, extract_images, pdf_path, output_dir)
    
    # 异步生成Markdown报告
    md_path = await generate_markdown_report_async(text_path, image_paths, output_dir)
    
    print(f"处理完成! 所有文件已保存到: {output_dir}")
    return text_path, image_paths, md_path

def process_pdf(pdf_path, output_dir=None):
    """
    处理PDF文件，提取文本和图片，生成Markdown报告
    
    Args:
        pdf_path (str): PDF文件路径
        output_dir (str, optional): 输出目录，如果不指定则使用当前目录
    
    Returns:
        tuple: (文本文件路径, 图片路径列表, Markdown报告路径)
    """
    return asyncio.run(process_pdf_async(pdf_path, output_dir))

def main():
    """命令行入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="使用pdfplumber处理PDF，提取文本和图片，生成Markdown报告")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output", help="输出目录(可选)", default=None)
    
    args = parser.parse_args()
    process_pdf(args.pdf_path, args.output)

if __name__ == "__main__":
    main()
