"""
#### 使用说明：

此代码提供了一个完整的图像文本处理工具，包括以下主要功能：

1. 图像到文本的转换（OCR和描述）
2. Base64编码转换
3. Markdown内容提取和处理
4. 文件保存功能

#### 主要功能：
- 将图像文件转换为Base64编码字符串
- 从文本中提取Markdown内容
- 描述图像内容，生成基于图像的Markdown描述
- 使用OCR从图像中提取文本内容
- 将提取的内容保存为Markdown文件
- 支持多种图像处理细节级别
- 支持自定义提示和模型选择

#### 注意事项：
- 请确保正确配置API密钥
- 运行时需要系统有足够的权限来创建目录并写入文件
- 支持多种图像格式（PNG、JPG、TIFF等）
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
from typing import Any, Dict
from pathlib import Path
from PIL import Image
from loguru import logger


class ImageTextExtractor:
    """图像文本提取器类，用于将图像内容转换为文本或Markdown格式。"""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.siliconflow.cn/v1",
        prompt: str | None = None,
        prompt_path: str | None = None,
    ):
        """
        初始化ImageTextExtractor实例。

        Args:
            api_key (str): API密钥，如果未提供则从环境变量中读取
            base_url (str): API基础URL
            prompt (str): 提示文本
            prompt_path (str): 提示文本文件路径
        """
        load_dotenv()
        self.api_key: str = api_key or os.getenv("API_KEY")

        if not self.api_key:
            raise ValueError("API key is required")

        self.client: OpenAI = OpenAI(
            api_key=self.api_key,
            base_url=base_url,
        )
        self._prompt: str = (
            prompt or self._read_prompt(prompt_path)
            if prompt_path
            else None
            or """
# OCR图像到Markdown转换提示

## 任务
将图像内容转换为markdown格式，特别处理文本、公式和结构化内容。

## 背景
- 图像可能包含混合内容，包括文本、数学公式、表格和图表
- 需要准确的OCR文本提取和公式识别
- 输出应为格式良好的markdown，便于集成

## 输入
- 任何包含文本、公式、图表或混合内容的图像
- 常见格式：PNG、JPG、TIFF
- 各种类型：文档扫描、截图、书写内容的照片

## 输出
- 保留原始结构的干净markdown文本
- 数学公式用$$分隔符括起来
- 示例：
    ```markdown
    # 检测到的标题

    常规文本内容...

    $$E = mc^2$$

    更多文本和内容...
    ```
            """
        )

    def _read_prompt(self, prompt_path: str) -> str:
        """
        从文件中读取提示文本。

        Args:
            prompt_path (str): 提示文本文件路径

        Returns:
            str: 提示文本内容
        """
        if not prompt_path.endswith((".md", ".txt")):
            raise ValueError("Prompt file must be a .md or .txt file")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def extract_image_text(
        self,
        image_url: str = None,
        local_image_path: str = None,
        model: str = "Qwen/Qwen2-VL-72B-Instruct",
        detail: str = "low",
        prompt: str = None,
        temperature: float = 0.1,
        top_p: float = 0.5,
    ) -> str:
        """
        提取图像中的文本并转换为Markdown格式。

        Args:
            image_url (str): 图像的URL
            local_image_path (str): 本地图像文件路径
            model (str): 使用的模型名称
            detail (str): 细节级别，允许值为'low', 'high', 'auto'
            prompt (str): 提示文本
            temperature (float): 生成文本的温度参数
            top_p (float): 生成文本的top_p参数

        Returns:
            str: 提取的Markdown格式文本
        """
        if not image_url and not local_image_path:
            raise ValueError("Either image_url or local_image_path is required")

        if image_url and not (
            image_url.startswith("http://")
            or image_url.startswith("https://")
            or self._is_base64(image_url)
        ):
            raise ValueError("Image URL must be a valid HTTP/HTTPS URL or a Base64 encoded string")

        if local_image_path:
            if not os.path.exists(local_image_path):
                raise FileNotFoundError(f"The file {local_image_path} does not exist.")
            image_extension: str = self._get_image_extension(local_image_path)
            with open(local_image_path, "rb") as image_file:
                base64_image: str = base64.b64encode(image_file.read()).decode("utf-8")
                image_url = f"data:image/{image_extension};base64,{base64_image}"

        if detail not in ["low", "high", "auto"]:
            raise ValueError("Invalid detail value. Allowed values are 'low', 'high', 'auto'")

        if detail == "auto":
            detail = "low"

        prompt = prompt or self._prompt

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url, "detail": detail},
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                stream=True,
                temperature=temperature,
                top_p=top_p,
            )

            result: str = ""
            for chunk in response:
                chunk_message: str = chunk.choices[0].delta.content
                result += chunk_message
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from image: {e}")

    def _is_base64(self, s: str) -> bool:
        """
        检查字符串是否为Base64编码。

        Args:
            s (str): 待检查的字符串

        Returns:
            bool: 如果是Base64编码则返回True，否则返回False
        """
        try:
            if isinstance(s, str):
                if s.strip().startswith("data:image"):
                    return True
                return base64.b64encode(base64.b64decode(s)).decode("utf-8") == s
            return False
        except Exception:
            return False

    def _get_image_extension(self, file_path: str) -> str:
        """
        获取图像文件的扩展名。

        Args:
            file_path (str): 图像文件路径

        Returns:
            str: 图像文件的扩展名
        """
        try:
            with Image.open(file_path) as img:
                return img.format.lower()
        except Exception as e:
            raise ValueError(f"Failed to determine image format: {e}")


def image_to_base64(image_path: str) -> str:
    """
    将图像文件转换为Base64编码的字符串。

    Args:
        image_path (str): 图像文件路径

    Returns:
        str: Base64编码的字符串
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def extract_markdown_content(text: str) -> str:
    """
    从文本中提取Markdown内容。

    Args:
        text (str): 输入文本

    Returns:
        str: 提取的Markdown内容，如果没有找到Markdown标记，则返回原始文本
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
    description_prompt_path: str = None,
) -> str:
    """
    描述图像的内容。

    Args:
        image_path (str): 图像文件路径
        api_key (str): API密钥
        model (str): 使用的模型名称
        prompt (str): 描述的提示信息
        description_prompt_path (str): 描述提示文件路径

    Returns:
        str: 图像内容描述
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
    api_key: str = None,
    model: str = "Qwen/Qwen2-VL-72B-Instruct",
    prompt: str = None,
    ocr_prompt_path: str = None,
) -> str:
    """
    从图像中提取文本内容（OCR）。

    Args:
        image_path (str): 图像文件路径
        api_key (str): API密钥
        model (str): 使用的模型名称
        prompt (str): OCR的提示信息
        ocr_prompt_path (str): OCR提示文件路径

    Returns:
        str: 提取的文本内容
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

    Args:
        content (str): 要保存的内容
        path (str): 文件路径，默认为'results/result.md'
    """
    output_dir = os.path.dirname(path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = path

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"结果已保存到文件: {output_path}")
