"""
#### 使用说明：

1. 调用 `add_image_description(path, force_add_desc=True)` 函数，传入要处理的目录路径。
2. 该函数将递归处理目录下所有Markdown文件中的图片描述。

#### 主要功能：

- 读取指定路径下的所有Markdown文件。
- 为Markdown文件中无描述的图片添加AI生成的描述。
- 可选择是否强制为所有图片添加描述。

#### 参数说明：

- `read_markdown_files(path)`
  - 参数:
    - `path`: str 或 Path对象，指定要搜索的目录或文件路径。
  - 返回:
    - list: 包含所有找到的Markdown文件路径的列表。

- `process_markdown_image(file_path, force_add_desc=False)`
  - 参数:
    - `file_path`: str, Markdown文件的路径。
    - `force_add_desc`: bool, 是否强制为所有图片添加描述。
  - 副作用:
    - 修改原始Markdown文件。
    - 在控制台输出处理状态。

- `add_md_image_description(path, force_add_desc=True)`
  - 参数:
    - `path`: str, 要处理的目录路径。
  - 副作用:
    - 处理目录下所有Markdown文件中的图片描述。

#### 注意事项：

- 路径必须是绝对路径。
- 依赖 `describe_image` 函数，需要确保该函数可用。

"""

import os  # 用于文件和目录操作
import re  # 用于正则表达式处理
from pathlib import Path  # 用于跨平台的路径操作
from tools.everything_to_text.image_to_text import describe_image
from loguru import logger


def read_markdown_files(path):
    """
    读取指定路径下的所有Markdown文件

    参数:
        path: str 或 Path对象，指定要搜索的目录或文件路径

    返回:
        list: 包含所有找到的Markdown文件路径的列表
    """
    path = Path(path).resolve()  # 转换为绝对路径
    if not path.is_absolute():
        raise ValueError("路径必须是绝对路径")
    # 如果输入路径是文件且为Markdown格式，直接返回该文件路径
    if path.is_file() and path.suffix.lower() in (".md", ".markdown"):
        return [str(path)]
    # 递归搜索目录下所有Markdown文件
    return [str(p) for p in path.rglob("*") if p.suffix.lower() in (".md", ".markdown")]


def process_markdown_image(file_path, force_add_desc=False, prompt=None):
    """
    处理单个Markdown文件，为无描述的图片添加AI生成的描述

    参数:
        file_path: str, Markdown文件的路径
        force_add_desc: bool, 是否强制为所有图片添加描述

    副作用:
        - 修改原始Markdown文件
        - 在控制台输出处理状态
    """
    prompt = (
        prompt
        or """
# 图像内容描述提示

## 任务
使用视觉语言模型生成图像内容的详细描述。

## 背景
- 视觉语言模型可以处理图像并生成文本描述
- 需要结构化输出以实现一致的图像分析
- 关注关键视觉元素及其关系

## 输入
- 图像格式：JPG、PNG或类似的视觉格式
- 图像内容：任何视觉场景、物体或构图

## 输出
请描述图像的以下方面：
1. 场景中的主要主体/物体
2. 元素之间的空间关系
3. 颜色和视觉特征
4. 动作或活动（如果有）
5. 环境背景
6. 任何文本或符号
7. 整体场景构图

示例模板：
"这张图片显示了[主要主体]在[位置]。[物体]是[空间关系]。主要颜色是[颜色]。[关于动作/背景的其他详细信息]。"

    """
    )
    try:
        file_path = Path(file_path).resolve()  # 转换为绝对路径
        if not file_path.is_absolute():
            raise ValueError("文件路径必须是绝对路径")

        # 读取Markdown文件内容
        with open(file_path, "r", encoding="utf-8") as f:
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

                    # 使用正则表达式去除描述中的特殊字符
                    new_desc = re.sub(
                        r"[\[\]\|\n\<\>\{\}\(\)\\\#\*`]",
                        "",
                        describe_image(full_path, prompt=prompt),
                    )
                    modified = True
                    return f"![{new_desc}]({img_path})"
            return match.group(0)

        # 使用正则表达式匹配并替换图片标记
        pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")
        new_content = pattern.sub(desc_replacer, content)

        # 如果文件被修改，写入新内容
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            logger.info(f"已更新文件: {file_path}")
        else:
            logger.info(f"无需修改: {file_path}")

    except Exception as e:
        logger.error(f"处理文件 {file_path} 时出错: {str(e)}")


def add_md_image_description(path, force_add_desc=True):
    """
    主处理流程

    参数:
        path: str, 要处理的目录路径

    副作用:
        处理目录下所有Markdown文件中的图片描述
    """
    path = Path(path).resolve()  # 转换为绝对路径
    if not path.is_absolute():
        raise ValueError("路径必须是绝对路径")

    for md_file in read_markdown_files(path):
        logger.info(f"正在处理: {md_file}")
        process_markdown_image(md_file, force_add_desc=force_add_desc)
