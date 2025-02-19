# 导入所需的标准库
import os  # 用于文件和目录操作
import re  # 用于正则表达式处理
from pathlib import Path  # 用于跨平台的路径操作

def read_markdown_files(path):
    """
    读取指定路径下的所有Markdown文件
    
    参数:
        path: str 或 Path对象，指定要搜索的目录或文件路径
        
    返回:
        list: 包含所有找到的Markdown文件路径的列表
    """
    path = Path(path).resolve()  # 转换为绝对路径
    # 如果输入路径是文件且为Markdown格式，直接返回该文件路径
    if path.is_file() and path.suffix.lower() in ('.md', '.markdown'):
        return [str(path)]
    # 递归搜索目录下所有Markdown文件
    return [str(p) for p in path.rglob('*') if p.suffix.lower() in ('.md', '.markdown')]

def process_markdown_image(file_path, force_add_desc=False):
    """
    处理单个Markdown文件，为无描述的图片添加AI生成的描述
    
    参数:
        file_path: str, Markdown文件的路径
        force_add_desc: bool, 是否强制为所有图片添加描述
        
    副作用:
        - 修改原始Markdown文件
        - 在控制台输出处理状态
    """
    try:
        # 读取Markdown文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 获取Markdown文件所在目录路径
        markdown_dir = os.path.dirname(file_path)
        modified = False  # 标记文件是否被修改

        def desc_replacer(match):
            """
            闭包函数：处理每个匹配到的图片标记
            
            参数:
                match: re.Match对象，包含匹配到的图片标记信息
                
            返回:
                str: 处理后的图片标记字符串
            """
            nonlocal modified
            desc, img_path = match.groups()
            # 当强制添加描述或原描述为空时处理
            if force_add_desc or not desc.strip():
                # 构建图片的完整路径
                full_path = os.path.normpath(os.path.join(markdown_dir, img_path))
                if os.path.exists(full_path):
                    new_desc = vlm_description(full_path)
                    modified = True
                    return f'![{new_desc}]({img_path})'
            return match.group(0)

        # 使用正则表达式匹配并替换图片标记
        pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
        new_content = pattern.sub(desc_replacer, content)

        # 如果文件被修改，写入新内容
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"已更新文件: {file_path}")
        else:
            print(f"无需修改: {file_path}")

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")

def vlm_description(image_path):
    """
    使用视觉语言模型生成图片描述
    
    参数:
        image_path: str, 图片文件的路径
        
    返回:
        str: 生成的图片描述
    """
    # TODO: 替换为实际的模型调用
    return f"图片描述 - {os.path.basename(image_path)}"

def add_image_description(path):
    """
    主处理流程
    
    参数:
        path: str, 要处理的目录路径
        
    副作用:
        处理目录下所有Markdown文件中的图片描述
    """
    for md_file in read_markdown_files(path):
        print(f"正在处理: {md_file}")
        process_markdown_image(md_file, force_add_desc=True)

