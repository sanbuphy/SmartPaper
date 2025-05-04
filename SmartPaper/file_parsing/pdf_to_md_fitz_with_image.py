import os
import fitz as pm
import re
from typing import Dict, List, Optional, Callable

from SmartPaper.file_parsing.image_utils.image_processing import (
    extract_images_info_from_layout,
    page2image, 
    sort_page_layout
)


def page_to_text(page_texts: Dict[int, str]) -> str:
    """
    将按页码存储的文本内容合并为完整的文档文本
    
    Args:
        page_texts: 按页码索引的文本字典，格式为 {页码: 文本内容}
    
    Returns:
        str: 合并后的完整文本
    """
    # 创建一个列表存储所有页面的文本
    markdown_content: List[str] = []
    
    # 按页码顺序添加文本内容
    for page_num in sorted(page_texts.keys()):
        markdown_content.append(page_texts[page_num])
    
    # 使用双换行符连接所有页面内容
    full_text: str = "\n\n".join(markdown_content)
    
    return full_text


def advanced_image_handler(page: pm.Page, page_num: int, output_dir: str, api_key: Optional[str] = None, 
                           delete_rendered_image: bool = True, cache_base64: bool = True, 
                           cache_dir: Optional[str] = None) -> str:
    """
    高级图像处理函数 - 处理PDF页面中的图像，提取并分析图像内容
    
    Args:
        page: PDF页面对象
        page_num: 页码（从1开始）
        output_dir: 输出目录
        api_key: 图像分析API密钥（可选）
        delete_rendered_image: 是否删除处理后的渲染页面图像，默认为True
        cache_base64: 是否缓存图像的base64编码，默认为True
        cache_dir: 缓存目录路径，若为None则使用默认目录
        
    Returns:
        str: 包含图像的Markdown文本
    """
    # 创建图像输出目录，确保它存在
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # 将PDF页面渲染为高质量图像，用于后续处理
    rendered_image_path = os.path.join(output_dir, f"page_{page_num}.png")
    page2image(page, rendered_image_path, zoom_factor=4.0)  # 4x缩放提供更好的图像质量
    
    # 分析页面布局并提取图像

    # 执行版面分析和排序
    layout_result = sort_page_layout(
        rendered_image_path=rendered_image_path,
        output_dir=output_dir,
        page_num=page_num-1  # 页码从0开始的内部表示
    )

    # 定义可识别的图像标签类型
    image_labels = {"image", "图片", "table", "表格", "chart", "图表"}

    # 从布局中提取图像并生成Markdown
    image_markdown = extract_images_info_from_layout(
        layout_result=layout_result,
        rendered_image_path=rendered_image_path,
        output_dir=output_dir,
        image_labels=image_labels,
        api_key=api_key,
        cache_base64=cache_base64,
        cache_dir=cache_dir
    )
        

    
    # 如果需要删除渲染后的页面图像
    if delete_rendered_image and os.path.exists(rendered_image_path):
        try:
            os.remove(rendered_image_path)
            print(f"已删除渲染图像: {rendered_image_path}")
        except Exception as e:
            print(f"删除渲染图像时发生错误: {e}")
    
    return image_markdown


def extract_pdf_content(
    pdf_path: str, 
    output_dir: str, 
    strip_references: bool = False,
    image_handler: Optional[Callable[[pm.Page, int, str, Optional[str], bool, bool, Optional[str]], str]] = None,
    api_key: Optional[str] = None,
    delete_rendered_images: bool = True,
    cache_base64: bool = True,
    cache_dir: Optional[str] = None
) -> str:
    """
    提取PDF文档内容，包括文本和图像，并生成Markdown文件
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
        strip_references: 是否去除参考文献部分
        image_handler: 图像处理函数，用于提取和处理图像
        api_key: 图像分析API密钥
        delete_rendered_images: 是否删除渲染后的页面图像
        cache_base64: 是否缓存图像的base64编码，默认为True
        cache_dir: 缓存目录路径，若为None则使用默认目录
        
    Returns:
        str: 生成的Markdown内容
    """
    # 打开PDF文档
    pdf_document: pm.Document = pm.open(pdf_path)

    # 存储每页的文本和图像内容
    page_texts: Dict[int, str] = {}
    page_images: Dict[int, str] = {}

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取PDF总页数
    total_pages: int = len(pdf_document)

    # 处理每一页内容
    references_found: bool = False
    for page_num in range(total_pages):
        # 获取当前页面对象
        page: pm.Page = pdf_document[page_num]
        
        # 提取页面文本
        current_page_text: str = page.get_text()
        
        # 如果提供了图像处理函数，则处理页面图像
        if image_handler is not None:
            image_markdown = image_handler(
                page, 
                page_num + 1, 
                output_dir, 
                api_key, 
                delete_rendered_images,
                cache_base64,
                cache_dir
            )
            page_images[page_num + 1] = image_markdown

        # 如果需要去除参考文献
        if strip_references:
            # 查找参考文献标记
            match: Optional[re.Match] = re.search(r"^\s*(References|参考文献)\s*$", current_page_text, re.IGNORECASE | re.MULTILINE)

            if match:
                # 找到参考文献部分，截断文本
                reference_start_index: int = match.start()
                current_page_text = current_page_text[:reference_start_index].rstrip()
                references_found = True

                # 保存截断后的文本
                page_texts[page_num + 1] = current_page_text
                print(f"Found references on page {page_num + 1}.")
          
                # 找到参考文献后就停止处理后续页面
                break 

        # 如果没有找到参考文献，或者不需要去除参考文献
        if not references_found:
            page_texts[page_num + 1] = current_page_text

    # 关闭PDF文档
    pdf_document.close()

    # 合并文本和图像内容生成最终的Markdown
    markdown_content: List[str] = []
    for page_num in sorted(page_texts.keys()):
        text_content = page_texts[page_num]
        image_content = page_images.get(page_num, "")
        
        # 如果页面有图像内容，将图像内容添加到文本后面
        if image_content:
            markdown_content.append(f"{text_content}\n\n{image_content}")
        else:
            markdown_content.append(text_content)
    
    # 生成完整的Markdown文本
    full_text: str = "\n\n".join(markdown_content)
    
    # 保存Markdown文件
    markdown_path = os.path.join(output_dir, "output.md")
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    # 打印保存信息
    print(f"已保存Markdown文件到: {markdown_path}")
    print(f"图像已保存到: {os.path.join(output_dir, 'images')}")

    return full_text


# 示例图像处理函数，保留但不使用
def default_image_handler(page: pm.Page, page_num: int, output_dir: str) -> None:
    """
    简单图像处理函数 - 将页面转换为图像并保存到指定目录
    此函数仅作为示例，实际使用advanced_image_handler
    
    Args:
        page: PDF页面对象
        page_num: 页码（从1开始）
        output_dir: 输出目录
    """
    # 将页面渲染为PNG图像，使用2x缩放提高质量
    pix = page.get_pixmap(matrix=pm.Matrix(2, 2))
    image_path = os.path.join(output_dir, f"page_{page_num}.png")
    pix.save(image_path)
    print(f"Saved image for page {page_num} to {image_path}")


