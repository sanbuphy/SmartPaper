"""
使用当前目录下的test_datas/test_page_1.png做为测试用的图像文件，
主要测试了视觉语言模型的描述功能和OCR功能。
此外还测试了保存结果到文件的功能。
"""

import sys
import os
import pytest


from tools.everything_to_text.image_to_text import (
    describe_image,
    save_result_to_file,
    extract_text_from_image,
    image_to_base64,
    extract_markdown_content,
)


@pytest.fixture
def image_path():
    current_file_dir = os.path.abspath(os.path.dirname(__file__))
    abs_file_path = os.path.join(current_file_dir, "test_datas/test_vlm_function_page_1.png")
    return abs_file_path


@pytest.fixture
def description_prompt():
    return """
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


@pytest.fixture
def ocr_prompt():
    return """
# OCR 图像到 Markdown 转换提示

## 任务
将图像内容转换为 markdown 格式，特别处理文本、公式和结构化内容。

## 背景
- 图像可能包含混合内容，包括文本、数学公式、表格和图表
- 需要准确的 OCR 文本提取和公式识别
- 输出应为格式良好的 markdown，便于集成

## 输入
- 任何包含文本、公式、图表或混合内容的图像
- 常见格式：PNG、JPG、TIFF
- 各种类型：文档扫描、截图、书写内容的照片

## 输出
- 保留原始结构的干净 markdown 文本
- 数学公式用 $$ 分隔符括起来
- 示例：
    ```markdown
    # 检测到的标题

    常规文本内容...

    $$E = mc^2$$

    更多文本和内容...
    ```
"""


def test_describe_image(image_path, description_prompt):
    description = describe_image(image_path, prompt=description_prompt)
    assert description is not None


def test_extract_text_from_image(image_path, ocr_prompt):
    extracted_text = extract_text_from_image(image_path, prompt=ocr_prompt)
    assert extracted_text is not None


def test_extract_markdown_content():
    text_with_markdown = "Some text before\n```markdown\nThis is markdown content\n```"
    text_without_markdown = "This is plain text"

    result_with_markdown = extract_markdown_content(text_with_markdown)
    result_without_markdown = extract_markdown_content(text_without_markdown)

    assert result_with_markdown == "This is markdown content"
    assert result_without_markdown == "This is plain text"


@pytest.fixture
def test_content():
    return "Test content"


def test_save_result_to_file_basic(tmp_path, test_content):
    # 测试基本文件保存功能
    test_file = tmp_path / "test_output.md"
    save_result_to_file(test_content, str(test_file))

    # 验证文件是否存在
    assert test_file.exists()

    # 验证内容是否正确保存
    with open(test_file, "r", encoding="utf-8") as f:
        saved_content = f.read()
    assert saved_content == test_content

    # 测试嵌套目录结构
    nested_path = tmp_path / "nested" / "dir" / "test.md"
    save_result_to_file(test_content, str(nested_path))
    assert nested_path.exists()


def test_save_result_to_file_default(test_content):
    # 测试默认路径保存
    default_path = "test_results/test_result.md"
    save_result_to_file(test_content)

    # 验证默认路径文件是否存在
    assert os.path.exists(default_path)

    # 清理测试文件
    os.remove(default_path)
    os.rmdir("test_results")
