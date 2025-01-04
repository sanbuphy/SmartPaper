"""
图像处理相关功能
包含：坐标处理、图像裁剪、PDF页面渲染等功能
主要用于将PDF文档中的图像提取出来，并进行分析和处理
"""

import os
import time
import uuid
import base64
from typing import List, Any, Union, Tuple, Optional, Dict
from PIL import Image
import pymupdf as pm

from SmartPaper.file_parsing.image_utils.layout_detect import LayoutDetector
from SmartPaper.file_parsing.image_utils.layout_sorter import LayoutSorter
from SmartPaper.file_parsing.image_utils.image_analysis import ImageAnalysis
from SmartPaper.file_parsing.image_utils.image_cache import ImageCache



def normalize_coordinates(coordinates: Any) -> List[Tuple[int, int]]:
    """
    标准化坐标格式为点列表[(x1,y1), (x2,y2)]
    
    Args:
        coordinates: 输入的坐标，可能有多种格式
        
    Returns:
        标准化后的坐标点列表
    """
    # 处理四个值的坐标格式 [x1, y1, x2, y2]
    if len(coordinates) == 4:
        # 转换为左上角和右下角坐标点
        x1, y1, x2, y2 = map(int, coordinates)
        return [(x1, y1), (x2, y2)]
        
    elif len(coordinates) == 2:
        # 处理两个点的坐标格式
        # 检查是否为点列表格式 [[x1,y1], [x2,y2]]
        if all(isinstance(p, (list, tuple)) and len(p) == 2 for p in coordinates):
            # 转换为整数坐标点
            return [(int(coordinates[0][0]), int(coordinates[0][1])), 
                    (int(coordinates[1][0]), int(coordinates[1][1]))]
        elif all(isinstance(p, (int, float)) for p in coordinates):
            # 如果是 [x, y] 单点格式，则创建一个默认的100x100区域
            x, y = map(int, coordinates)
            return [(x, y), (x + 100, y + 100)]
    
    # 无法识别的坐标格式，抛出异常
    raise ValueError(f"无法识别的坐标格式: {coordinates}")


def crop_image(
    image_path: str, box_coordinates: Any,
    return_image_path: bool = True, 
    output_filename: str = None,
    cache_base64: bool = False,
    cache_dir: Optional[str] = None
) -> Union[str, Image.Image]:
    """
    根据坐标裁剪图像区域
    
    Args:
        image_path: 图像文件路径
        box_coordinates: 裁剪框坐标（支持多种格式，会通过normalize_coordinates进行标准化）
        return_image_path: 是否返回保存后的图像路径，否则返回图像对象
        output_filename: 输出文件名(包含后缀)，若提供则使用该名称，否则自动生成
        cache_base64: 是否缓存base64编码
        cache_dir: 缓存目录路径，若为None则使用默认目录
    
    Returns:
        裁剪后的图像路径或图像对象
    """
    # 打开原始图像
    image = Image.open(image_path)
    
    # 标准化坐标格式为[(x1,y1), (x2,y2)]格式
    points = normalize_coordinates(coordinates=box_coordinates)
    
    # 从点集合中提取x和y坐标，确定裁剪边界
    x_coordinates = [point[0] for point in points]
    y_coordinates = [point[1] for point in points]
    
    # 确定裁剪区域的左上角和右下角
    left, top = min(x_coordinates), min(y_coordinates)
    right, bottom = max(x_coordinates), max(y_coordinates)
    
    # 确保坐标不超出图像边界
    width, height = image.size
    left = max(0, left)
    top = max(0, top)
    right = min(width, right)
    bottom = min(height, bottom)
    
    # 执行裁剪操作
    cropped = image.crop((left, top, right, bottom))
    
    if return_image_path:
        # 需要保存裁剪后的图像
        output_dir = "output/crops"
        os.makedirs(output_dir, exist_ok=True)
        
        # 确定输出文件名
        if output_filename:
            # 使用指定的文件名
            cropped_path = os.path.join(output_dir, output_filename)
        else:
            # 使用时间戳生成唯一文件名
            timestamp = int(time.time() * 1000)
            cropped_path = os.path.join(output_dir, f"cropped_image_{timestamp}.jpg")
            
        # 保存裁剪后的图像
        cropped.save(cropped_path)
        
        # 如果需要缓存base64编码
        if cache_base64:
            # 使用图像缓存工具缓存base64编码
            with ImageCache(cache_dir=cache_dir) as cache:
                cache.cache_image(cropped_path)
            
        # 返回保存的图像路径
        return cropped_path
    
    # 直接返回裁剪后的图像对象
    return cropped



def page2image(page, output_path, zoom_factor=4.0):
    """
    将PDF页面渲染为高质量图像并保存
    
    Args:
        page: PyMuPDF页面对象
        output_path: 输出图像的完整路径
        zoom_factor: 渲染的缩放因子，默认为4.0（相当于约288 DPI）
        
    Returns:
        str: 保存的图像路径
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 使用缩放因子创建变换矩阵，提高图像质量
    mat = pm.Matrix(zoom_factor, zoom_factor)
    
    # 创建像素图并保存（不使用alpha通道）
    pix = page.get_pixmap(matrix=mat, alpha=False)
    pix.save(output_path)
    
    print(f"已保存图像: {output_path}")
    
    return output_path


def sort_page_layout(rendered_image_path, output_dir, page_num):
    """
    分析页面布局并返回排序后的结果
    使用LayoutDetector进行版面检测，再用LayoutSorter进行排序

    Args:
        rendered_image_path: 渲染后的页面图像路径
        output_dir: 输出目录，用于保存布局检测结果
        page_num: 页码，用于生成输出文件名

    Returns:
        dict: 排序后的版面分析结果
    """
    # 初始化文档版面分析器
    detector = LayoutDetector()
    
    # 执行版面检测，并将结果保存到JSON文件
    layout_result = detector.detect_layout(
        image_path=rendered_image_path,
        output_path=os.path.join(output_dir, f"layout_detection_page_{page_num + 1}.json"),
    )

    # 初始化版面排序器并执行排序
    sorter = LayoutSorter()
    
    # 返回排序后的布局结果
    return sorter.sort_layout(layout_result=layout_result, image_path=rendered_image_path)


def process_image_box(box, rendered_image_path, output_dir, api_key=None, cache_base64=True, cache_dir=None):
    """
    处理单个图像框 - 进行图像提取、保存和分析，返回图像信息
    
    Args:
        box: 图像框信息，包含坐标等数据
        rendered_image_path: 渲染后的页面图像路径
        output_dir: 图像输出目录
        api_key: 图像分析API密钥，用于调用图像分析服务
        cache_base64: 是否缓存图像的base64编码
        cache_dir: 缓存目录路径，若为None则使用默认目录
        
    Returns:
        dict: 图像信息字典，包含路径、描述、标题等信息
    """
    # 获取图像框坐标
    coordinate = box["coordinate"]
    
    # 使用UUID生成唯一的文件名，避免文件名冲突
    image_filename = f"{uuid.uuid4().hex}.jpg"
    
    # 确保图像输出目录存在
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # 构建图像的最终保存路径
    new_image_path = os.path.join(images_dir, image_filename)
    
    # 裁剪图片并保存
    cropped_image = crop_image(
        image_path=rendered_image_path, 
        box_coordinates=coordinate, 
        return_image_path=False  # 返回图像对象而不是路径
    )
    
    # 将裁剪后的图像直接保存到最终位置
    cropped_image.save(new_image_path)
    
    # 如果启用缓存，将图像缓存为base64编码
    if cache_base64:
        with ImageCache(cache_dir=cache_dir) as cache:
           key =  cache.cache_image(new_image_path)
    print(f"缓存图像: {new_image_path}")
    with ImageCache(cache_dir=cache_dir) as cache:
        base64_data = cache.get_base64_image(key=key)
        print(f"base64数据长度: {len(base64_data)}")

    # 使用图像分析API分析图像内容
    image_analyzer = ImageAnalysis(api_key=api_key)
    analysis_result = image_analyzer.analyze_image(local_image_path=new_image_path)
    description = analysis_result.get("description", "")  # 图像描述
    title = analysis_result.get("title", "图像")  # 图像标题
    
    # 创建包含图像所有信息的字典（不包含base64编码）
    image_info = {
        'path': new_image_path,  # 图片绝对路径，用于程序内部引用
        'rel_path': os.path.join("./images", image_filename),  # 相对路径，用于Markdown引用
        'description': description,  # 图片描述
        'title': title,  # 图片标题
        'image_key': image_filename  # 图片唯一标识，使用文件名
    }
    
    return image_info


def extract_images_info_from_layout(layout_result, rendered_image_path, output_dir, image_labels, api_key=None, cache_base64=True, cache_dir=None):
    """
    从布局结果中提取所有图像，并生成对应的Markdown文本
    
    Args:
        layout_result: 版面分析结果，包含各种元素的边界框
        rendered_image_path: 渲染后的页面图像路径
        output_dir: 图像输出目录
        image_labels: 图像标签集合，用于筛选图像类型的元素
        api_key: 图像分析API密钥
        cache_base64: 是否缓存图像的base64编码
        cache_dir: 缓存目录路径，若为None则使用默认目录
        
    Returns:
        str: 图像的Markdown文本表示
    """
    # 初始化Markdown文本和图像信息列表
    image_markdown = ""
    image_infos = []  # 存储所有处理过的图像信息，但不包含在返回值中
    
    # 检查布局结果中是否包含边界框
    if "boxes" in layout_result:
        # 筛选出属于图像类型的边界框
        
        boxes = [box for box in layout_result["boxes"] if box["label"] in image_labels]
        
        if boxes:
            # 处理每个图像边界框
            for box in boxes:
                # 提取和处理图像
                image_info = process_image_box(
                    box=box,
                    rendered_image_path=rendered_image_path,
                    output_dir=output_dir,
                    api_key=api_key,
                    cache_base64=cache_base64,
                    cache_dir=cache_dir
                )
                
                # 从图像信息中提取数据，用于生成Markdown
                title = image_info.get('title', '图像')
                description = image_info.get('description', '')
                rel_path = image_info['rel_path']  # 相对路径，格式为./images/filename.jpg
                
                # 生成图像的Markdown表示
                image_markdown += f"![{title}]({rel_path})\n\n> {description}\n\n"
                
                # 将图像信息添加到列表中，以便后续处理
                image_infos.append(image_info)

    # 返回所有图像的Markdown表示
    return image_markdown



