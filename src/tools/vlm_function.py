from dotenv import load_dotenv
import base64
import sys
import os

# 将父目录添加到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.image2text import ImageTextExtractor


def image_to_base64(image_path: str) -> str:
    """
    将图像文件转换为Base64编码的字符串。

    参数:
    image_path (str): 图像文件路径。

    返回:
    str: Base64编码的字符串。
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def extract_markdown_content(text: str) -> str:
    """
    从文本中提取Markdown内容。

    参数:
    text (str): 输入文本。

    返回:
    str: 提取的Markdown内容，如果没有找到Markdown标记，则返回原始文本。
    """
    start_marker = "```markdown"
    end_marker = "```"

    start_index = text.find(start_marker)
    if start_index == -1:
        return text.strip() if text else None

    start_index += len(start_marker)
    end_index = text.find(end_marker, start_index)

    if end_index == -1:
        return text[start_index:].strip()
    return text[start_index:end_index].strip()


def describe_image(
    image_path: str,
    api_key: str = None,
    model: str = "Qwen/Qwen2-VL-72B-Instruct",
    prompt: str = None,
    description_prompt_path: str = "description_prompt.md",
) -> str:
    """
    描述图像的内容。

    参数:
    image_path (str): 图像文件路径。
    model (str): 使用的模型名称，默认值为 "Qwen/Qwen2-VL-72B-Instruct"。
    description_prompt_path (str): 描述提示文件路径。

    返回:
    str: 图像内容描述。
    """
    extractor = ImageTextExtractor(
        api_key=api_key, prompt=prompt, prompt_path=description_prompt_path
    )

    try:
        result = extractor.extract_image_text(
            local_image_path=image_path, model=model, detail="low"
        )
        if not result.strip():
            return None
        return extract_markdown_content(result)
    except Exception as e:
        return f"描述图像时出错: {str(e)}"


def extract_text_from_image(
    image_path: str,
    model: str = "Qwen/Qwen2-VL-72B-Instruct",
    prompt: str = None,
    ocr_prompt_path: str = "ocr_prompt.md",
) -> str:
    """
    从图像中提取文本内容（OCR）。

    参数:
    image_path (str): 图像文件路径。
    model (str): 使用的模型名称，默认值为 "Qwen/Qwen2-VL-72B-Instruct"。
    ocr_prompt_path (str): OCR提示文件路径。

    返回:
    str: 提取的文本内容。
    """
    extractor = ImageTextExtractor(api_key=api_key, prompt=prompt, prompt_path=ocr_prompt_path)

    try:
        result = extractor.extract_image_text(
            local_image_path=image_path, model=model, detail="low"
        )
        if not result.strip():
            return None
        return extract_markdown_content(result)
    except Exception as e:
        return f"提取文本时出错: {str(e)}"


def save_result_to_file(content: str, path: str = "results/result.md"):
    """
    将内容保存到文件。

    参数:
    content (str): 要保存的内容。
    path (str): 文件路径，默认值为 'results/result.md'。
    """
    output_dir = os.path.dirname(path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = path

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"结果已保存到文件: {output_path}")
