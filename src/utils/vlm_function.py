from dotenv import load_dotenv
import base64
import sys
import  os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.image2text import ImageTextExtractor

# 加载环境变量
load_dotenv()
api_key: str = os.getenv('API_KEY')


def image_to_base64(image_path: str) -> str:
    """
    将图像文件转换为Base64编码字符串

    参数:
    image_path (str): 图像文件路径

    返回:
    str: Base64编码字符串
    """
    with open(image_path, "rb") as image_file:
        encoded_string: str = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def extract_markdown_content(text: str) -> str:
    """
    从文本中提取Markdown内容

    参数:
    text (str): 输入文本

    返回:
    str: 提取的Markdown内容，如果没有找到Markdown标记则返回原文本
    """
    start_marker: str = "```markdown"
    end_marker: str = "```"

    start_index: int = text.find(start_marker)
    if start_index == -1:
        if len(text):
            return text.strip()
        return None

    start_index += len(start_marker)
    end_index: int = text.find(end_marker, start_index)

    if end_index == -1:
        return text[start_index:].strip()
    return text[start_index:end_index].strip()


def describe_image(image_path: str,
                   model: str = "Qwen/Qwen2-VL-72B-Instruct",
                   description_prompt_path: str = "description_prompt.md") -> str:
    """
    描述图像内容

    参数:
    image_path (str): 图像文件路径
    model (str): 使用的模型名称，默认值为 "Qwen/Qwen2-VL-72B-Instruct"

    返回:
    str: 图像内容描述
    """

    extractor: ImageTextExtractor = ImageTextExtractor(api_key=api_key, prompt_path=description_prompt_path)

    try:
        result: str = extractor.extract_image_text(local_image_path=image_path, model=model, detail="low")
        if not result.strip():
            return "No description generated for the image"
        return extract_markdown_content(result)
    except Exception as e:
        return f"Error describing image: {str(e)}"


def extract_text_from_image(image_path: str,
                            model: str = "Qwen/Qwen2-VL-72B-Instruct",
                            ocr_prompt_path: str = "ocr_prompt.md"
                            ) -> str:
    """
    从图像中提取文本内容（OCR）

    参数:
    image_path (str): 图像文件路径
    model (str): 使用的模型名称，默认值为 "Qwen/Qwen2-VL-72B-Instruct"

    返回:
    str: 提取的文本内容
    """
    extractor: ImageTextExtractor = ImageTextExtractor(api_key=api_key, prompt_path=ocr_prompt_path)

    try:
        result: str = extractor.extract_image_text(local_image_path=image_path, model=model, detail="low")
        if not result.strip():
            return "No text extracted from the image"
        return extract_markdown_content(result)
    except Exception as e:
        return f"Error extracting text: {str(e)}"


def save_result_to_file(content: str, filename: str = 'result.md'):
    """
    将内容保存到文件

    参数:
    content (str): 要保存的内容
    filename (str): 文件名，默认值为 'result.md'
    """
    output_dir: str = 'results'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path: str = os.path.join(output_dir, filename)

    with open(output_path, 'w', encoding="utf-8") as f:
        f.write(content)
    print(f"结果已保存到文件: {output_path}")



