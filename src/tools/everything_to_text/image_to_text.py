"""
#### 使用说明：

1. 初始化 `ImageTextExtractor` 实例时可以传入 `api_key`、`base_url`、`prompt` 或 `prompt_path`。
2. 使用 `extract_image_text` 方法可以提取图像中的文本并转换为 Markdown 格式。
3. 使用 `get_image_title` 函数可以为图像描述生成简短的标题。
4. 提供多种图像处理功能：`extract_text_from_image`、`describe_image`、`extract_table_from_image`。

#### 主要功能：
- 初始化时可以从环境变量读取 API 密钥，或者手动传入。
- 提供了从文件读取自定义提示文本的功能。
- 支持提取图像 URL 或本地图像文件路径中的文本。
- 将提取的文本转换为 Markdown 格式，包括数学公式的格式化。
- 支持图像 URL 或 Base64 编码图像的解析。
- 提供多种模型和生成文本的细节级别设置。
- 生成图像的描述性标题。
- 提取图像中的表格并转换为Markdown或HTML格式。

#### 主要组件：
- `ImageTextExtractor`类：核心图像文本提取功能
- `get_image_title`函数：生成图像标题
- 多种图像处理函数：文本提取、图像描述、表格提取
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
load_dotenv()
# 默认提示文本
_prompt = """
你是一个可以识别图片的AI，你可以基于图片与用户进行友好的对话。
"""

# 图像标题生成的系统提示
SYSTEM_PROMPT = """你是一个专业图像标题生成助手。
任务：根据提供的图像描述生成一个简短、准确且具有描述性的标题。

输出要求：
- 标题应简洁（通常控制在5-20个字之间）
- 突出图像的核心主题或最显著特征
- 使用具体而非抽象的词语
- 不要包含"这是"、"这张图片"等冗余词语
- 学术论文或技术图像应保留专业术语的准确性
- 直接输出标题文本，无需额外说明或引号

示例：
描述：茂密森林中，阳光透过树叶洒落在地面，形成斑驳光影。远处小溪流淌，水面反射着周围绿色植被。
标题：晨光森林溪流

描述：年轻女性在实验室使用显微镜观察样本。她穿白色实验服，戴护目镜，专注调整显微镜。旁边放着试管和实验笔记。
标题：科研人员显微观察

描述：学术论文封面，白色背景。标题"ISAM-MTL: Cross-subject multi-task learning model with identifiable spikes and associative memory networks"位于顶部，黑色字体。下方是作者名字"Junyan Li", "Bin Hu", "Zhi-Hong Guan"。摘要部分介绍EEG信号跨主体变化性和ISAM-MTL模型。页面右下角显示DOI和版权信息。
标题：ISAM-MTL 论文封面首页
"""

# 图像标题生成的用户提示模板
USER_PROMPT_TEMPLATE = """基于以下图像描述，提供一个简洁、专业的标题：
----
描述：{description}
----
直接输出标题（5-15字）："""

# 各种图像处理的提示文本
ocr_prompt = """
使用OCR的模式提取图像中的文本内容，并转换为Markdown格式。
注意：不要输出图片以外的内容。
其中表格输出为Markdown格式，或者html格式，公式输出为带有$或者$$风格的LaTeX格式。
"""

description_prompt = """
# PDF图像内容描述提示

## 任务

使用视觉语言模型生成从PDF提取的图像内容的简洁描述。

## 背景

- 图像来源于PDF文档
- 需要清晰理解图像的主要内容和用途
- 避免冗余描述，保持精简

## 输入

- 从PDF提取的图像

## 输出

请简洁描述图像的以下关键方面：

1. 图像类型（图表、示意图、照片等）
2. 主要内容/主题
3. 包含的关键信息点
4. 文本或标签（如有）
5. 图像的可能用途

示例格式：
"这是一张[图像类型]，展示了[主要内容]。包含[关键信息]。[其他相关细节]。"
"""

extract_table_prompt = """
提取图片当中的表格，并输出为支持markdown格式的html语法。
注意：不要输出图片以外的内容。
"""

def extract_markdown_content(text: str) -> str:
    """
    从文本中提取Markdown内容，自动去除markdown和html代码块标记。

    参数:
    text (str): 输入文本。

    返回:
    str: 提取的内容，如果没有找到Markdown或HTML标记，则返回原始文本。
    """
    md_start_marker = "```markdown"
    html_start_marker = "```html"
    end_marker = "```"

    # 处理markdown代码块
    md_start_index = text.find(md_start_marker)
    if md_start_index != -1:
        start_index = md_start_index + len(md_start_marker)
        end_index = text.find(end_marker, start_index)
        
        if end_index == -1:
            return text[start_index:].trip()
        return text[start_index:end_index].strip()
    
    # 处理html代码块
    html_start_index = text.find(html_start_marker)
    if html_start_index != -1:
        start_index = html_start_index + len(html_start_marker)
        end_index = text.find(end_marker, start_index)
        
        if end_index == -1:
            return text[start_index:].strip()
        return text[start_index:end_index].strip()
    
    # 如果没有找到特定标记，返回原始文本
    return text.strip() if text else None


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


class ImageTextExtractor:
    """
    图像文本提取器类，用于将图像内容转换为 Markdown 格式的文本。
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.siliconflow.cn/v1",
        prompt: str | None = None,
        prompt_path: str | None = None,
    ):
        """
        初始化 ImageTextExtractor 实例。

        :param api_key: API 密钥，如果未提供则从环境变量中读取
        :param base_url: API 基础 URL
        :param prompt: 提示文本
        :param prompt_path: 提示文本文件路径
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
            prompt or self._read_prompt(prompt_path)  or _prompt
        )

    def _read_prompt(self, prompt_path: str) -> str:
        """
        从文件中读取提示文本。

        :param prompt_path: 提示文本文件路径
        :return: 提示文本内容
        """
        if not prompt_path or not os.path.exists(prompt_path):
            return None
            
        if not prompt_path.endswith((".md", ".txt")):
            raise ValueError("Prompt file must be a .md or .txt file")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def extract_image_text(
        self,
        image_url: str = None,
        local_image_path: str = None,
        model: str = "Qwen/Qwen2.5-VL-72B-Instruct",
        detail: str = "low",
        prompt: str = None,
        temperature: float = 0.1,
    ) -> str:
        """
        提取图像中的文本并转换为 Markdown 格式。

        :param image_url: 图像的 URL
        :param local_image_path: 本地图像文件路径
        :param model: 使用的模型名称
        :param detail: 细节级别，允许值为 'low', 'high', 'auto'
        :param prompt: 提示文本
        :param temperature: 生成文本的温度参数
        :return: 提取的 Markdown 格式文本
        """

        if not image_url and not local_image_path:
            raise ValueError("Either image_url or local_image_path is required")

        if image_url and not (
            image_url.startswith("http://")
            or image_url.startswith("https://")
            or self._is_base64(image_url)
        ):
            raise ValueError(
                "Image URL must be a valid HTTP/HTTPS URL or a Base64 encoded string"
            )

        if local_image_path:
            if not os.path.exists(local_image_path):
                raise FileNotFoundError(f"The file {local_image_path} does not exist.")
            image_extension: str = self._get_image_extension(local_image_path)
            with open(local_image_path, "rb") as image_file:
                base64_image: str = base64.b64encode(image_file.read()).decode("utf-8")
                image_url = f"data:image/{image_extension};base64,{base64_image}"

        if detail not in ["low", "high", "auto"]:
            raise ValueError(
                "Invalid detail value. Allowed values are 'low', 'high', 'auto'"
            )

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
            )

            result: str = ""
            for chunk in response:
                chunk_message: str = chunk.choices[0].delta.content
                if chunk_message is not None:
                    result += chunk_message
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from image: {e}")

    def _is_base64(self, s: str) -> bool:
        """
        检查字符串是否为 Base64 编码。

        :param s: 待检查的字符串
        :return: 如果是 Base64 编码则返回 True，否则返回 False
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

        :param file_path: 图像文件路径
        :return: 图像文件的扩展名
        """
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                return img.format.lower()
        except Exception as e:
            raise ValueError(f"Failed to determine image format: {e}")


def get_image_title(image_description, api_key=None, base_url="https://api.siliconflow.com/v1"):
    """
    使用硅基流动的deepseek v3 为多模态提取的图片描述生成图片的标题。

    参数:
        image_description (str): 图像的描述文本
        api_key (str): 您的OpenAI API密钥
        base_url (str): API基础URL

    返回:
        str: 为图像生成的标题
    """

    if not api_key:
        api_key = os.getenv("API_KEY")
    # 使用Silicon Flow基础URL初始化客户端
    client = OpenAI(api_key=api_key, base_url=base_url)

    # 发送API请求
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(description=image_description),
            },
        ],
    )

    # 提取并返回标题
    title = response.choices[0].message.content.strip()
    return title


def _process_image_with_model(
    image_path: str,
    model: str="Qwen/Qwen2.5-VL-72B-Instruct",
    prompt_path: str = None,
    prompt_text: str = None,
    api_key: str = None,
    detail: str = "low",
    post_process_func = None
) -> str:
    """处理图像并返回模型输出的基础函数"""
    if api_key is None:
        api_key = os.getenv("API_KEY")
    
    extractor = ImageTextExtractor(
        api_key=api_key,
        prompt_path=prompt_path,
        prompt=prompt_text
    )

    try:
        result = extractor.extract_image_text(
            local_image_path=image_path, model=model, detail=detail
        )
        
        if not result.strip():
            return "No content extracted from the image"
        
        if post_process_func:
            return post_process_func(result)
        return extract_markdown_content(result)
    except Exception as e:
        return f"Error processing image: {str(e)}"


def extract_text_from_image(
    image_path: str,
    model: str = "Qwen/Qwen2.5-VL-72B-Instruct",
    ocr_prompt_path: str = None,
    api_key: str = None,
) -> str:
    """从图像中提取文本内容并转换为Markdown格式"""
    return _process_image_with_model(
        image_path=image_path,
        model=model,
        prompt_path=ocr_prompt_path,
        prompt_text=ocr_prompt if not ocr_prompt_path else None,
        api_key=api_key,
        detail="low"
    )


def describe_image(
    image_path: str,
    model: str = "Qwen/Qwen2.5-VL-72B-Instruct",
    description_prompt_path: str = None,
    api_key: str = None,
) -> str:
    """描述图像内容并生成文本描述"""
    return _process_image_with_model(
        image_path=image_path,
        model=model,
        prompt_path=description_prompt_path,
        prompt_text=description_prompt if not description_prompt_path else None,
        api_key=api_key,
        detail="low"
    )





def extract_table_from_image(
    image_path: str,
    model: str = "Qwen/Qwen2.5-VL-72B-Instruct",
    extract_table_prompt_path: str = None,
    api_key: str = None,
) -> str:
    """从图像中提取表格内容并转换为Markdown或HTML格式"""
    return _process_image_with_model(
        image_path=image_path,
        model=model,
        prompt_path=extract_table_prompt_path,
        prompt_text=extract_table_prompt if not extract_table_prompt_path else None,
        api_key=api_key,
        detail="high",
        post_process_func=extract_markdown_content
    )



if __name__ == "__main__" and __file__ == "image_to_text.py":
    image_description = """
    这张图片显示了一篇学术论文的封面。
    封面的背景是白色的，标题
    "ISAM-MTL: Cross-subject multi-task learning model with identifiable spikes and associative memory networks"
    位于页面的顶部，使用了黑色的字体。
    标题下方是作者的名字，分别是"Junyan Li", "Bin Hu", 和"Zhi-Hong Guan"。再往下是摘要部分，使用了较小的字体。
    摘要的标题是"Abstract"，内容是关于EEG（脑电图）信号的跨主体变化性，
    以及一种新的模型"ISAM-MTL"（Identifiable Spikes and Associative Memory Multi-Task Learning）的介绍。
    摘要的最后是"Introduction"部分的开头，介绍了脑机接 口（BCI）系统和EEG信号的相关背景。
    页面的右下角显示了论文的引用信息，包括DOI（数字对象标识符）和版权信息。
    整体构图简洁明了，信息层次分明。
    """
    title = get_image_title(image_description)
    print(title)
