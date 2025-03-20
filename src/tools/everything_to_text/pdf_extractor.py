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
import fitz  # PyMuPDF
import os
import asyncio
import concurrent.futures
import time
from datetime import datetime

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
        load_dotenv()
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
        detail="low",
        post_process_func=extract_markdown_content
    )



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
    
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    
    # 获取PDF文件名（不含扩展名）
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 输出文本文件路径
    output_text_path = os.path.join(output_dir, f"{pdf_name}_text.txt")
    
    # 提取文本
    with open(output_text_path, 'w', encoding='utf-8') as text_file:
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text()
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
    
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    
    # 获取PDF文件名（不含扩展名）
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 创建图片目录
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # 记录提取的图片文件路径
    image_paths = []
    
    # 遍历每一页
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # 获取页面上的图像
        image_list = page.get_images(full=True)
        
        # 遍历该页的图片
        for img_index, img in enumerate(image_list):
            xref = img[0]  # 图片的xref
            
            # 提取图像
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            
            # 确定图像扩展名
            ext = base_image["ext"]
            
            # 保存图像
            image_filename = f"page{page_num + 1}_img{img_index + 1}.{ext}"
            image_path = os.path.join(images_dir, image_filename)
            
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            image_paths.append(image_path)
    
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
    global total_images
    total_images = total  # 设置全局变量，供其他函数使用
    
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

async def process_page_images_async(page_images, output_dir):
    """
    异步处理页面中的所有图片
    """
    tasks = [process_image_async(img_path, output_dir) for img_path in page_images]
    return await asyncio.gather(*tasks)


    
    return title or f"图片{os.path.basename(image_path)}"

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

def generate_markdown_report(text_path, image_paths, output_dir):
    """
    生成包含文本和图片的Markdown报告
    
    Args:
        text_path (str): 提取的文本文件路径
        image_paths (list): 提取的图片文件路径列表
        output_dir (str): 输出目录
    
    Returns:
        str: 生成的Markdown文件路径
    """
    return asyncio.run(generate_markdown_report_async(text_path, image_paths, output_dir))

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

if __name__ == "__main__":
    # 这里可以直接调用process_pdf函数，例如：
    process_pdf("test.pdf", "./output")



