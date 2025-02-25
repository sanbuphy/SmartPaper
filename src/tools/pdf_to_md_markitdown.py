"""
#### 使用说明：

该代码实现了将不同格式文件转换为Markdown格式的功能，并且支持从URL下载文件并转换。

#### 主要功能：
- 初始化转换器，配置LLM客户端和模型。
- 支持多种文件格式的转换（如PDF、Word、Excel、图片等）。
- 从URL下载文件并转换为Markdown内容。
- 支持对PDF文件进行特殊处理（如处理arxiv.org上的PDF）。
- 对URL请求失败时，自动重试多次，带有指数退避。

#### 参数说明：

- **MarkdownConverter类构造函数**：
  - `llm_client (Any)`: LLM客户端，用于图像描述等高级功能。
  - `llm_model (str)`: LLM模型名称。
  - `config (Dict, optional)`: 配置信息（如最大请求次数等）。

- **convert函数**：
  - `file_path (str)`: 要转换的文件路径。
  - **返回值**：返回一个包含`text_content`（转换后的Markdown文本），`metadata`（附加元数据），以及`images`（转换过程中提取的图片）的字典。

- **convert_url函数**：
  - `url (str)`: 需要下载并转换的文件的URL。
  - `description (str, optional)`: 论文的描述，适用于arxiv.org的PDF文件。
  - **返回值**：返回一个包含`text_content`（转换后的Markdown文本），`metadata`（附加元数据），以及`images`（转换过程中提取的图片）的字典。

#### 注意事项：
- 请确保安装了`requests`、`mimetypes`、`markitdown`、`loguru`等依赖库。
- 支持的文件类型包括：PDF、Word、PPT、图片、HTML、CSV等常见格式。
- 下载文件时，存在重试机制，网络错误会自动重试。

#### 更多信息：
- 本转换器提供了LLM集成，可以对图像或复杂内容进行更深入的分析和描述。


"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import requests
import mimetypes
from markitdown import MarkItDown
from loguru import logger
import time


class MarkdownConverter:
    """通用文档转Markdown转换器"""

    def __init__(self, llm_client: Any = None, llm_model: str = None, config: Dict = None):
        """初始化转换器

        Args:
            llm_client (Any): LLM客户端,用于图像描述等高级功能
            llm_model (str): LLM模型名称
            config (Dict, optional): 配置信息
        """
        # 根据是否提供LLM客户端来初始化MarkItDown
        if llm_client and llm_model:
            self.md = MarkItDown(llm_client=llm_client, llm_model=llm_model)
        else:
            self.md = MarkItDown()
        logger.info("初始化MarkdownConverter完成")

        # 设置配置信息
        self.config = config or {}
        self.max_requests = self.config.get("llm", {}).get("max_requests", 3)

        # 支持的文件类型
        self.supported_extensions = {
            ".pdf",
            ".docx",
            ".pptx",
            ".xlsx",
            ".jpg",
            ".jpeg",
            ".png",
            ".txt",
            ".md",
            ".csv",
            ".json",
            ".yaml",
            ".yml",
            ".html",
            ".htm",
            ".zip",
            ".mp3",
            ".wav",
            ".xml",
        }

    def convert(self, file_path: str) -> Dict:
        """转换文件为Markdown

        Args:
            file_path (str): 文件路径

        Returns:
            Dict: 包含转换结果的字典
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        ext = file_path.suffix.lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"不支持的文件类型: {ext}")

        try:
            result = self.md.convert(str(file_path))

            return {"text_content": result.text_content, "metadata": {}, "images": []}
        except Exception as e:
            raise Exception(f"文件转换失败: {str(e)}")

    def convert_url(self, url: str, description: str = None) -> Dict:
        """从URL下载并转换文件

        Args:
            url (str): 文件URL
            description (str, optional): 论文描述

        Returns:
            Dict: 包含转换结果的字典
        """
        retry_count = 0
        while retry_count < self.max_requests:
            try:
                # 判断是否为PDF文件
                is_arxiv = "arxiv.org" in url.lower()

                if is_arxiv:
                    # 创建temp目录(如果不存在)
                    temp_dir = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp"
                    )
                    os.makedirs(temp_dir, exist_ok=True)

                    # 从URL提取文件名
                    arxiv_id = url.split("/")[-1]
                    if not arxiv_id.endswith(".pdf"):
                        arxiv_id += ".pdf"
                    temp_path = os.path.join(temp_dir, arxiv_id)

                    # 检查是否已存在同名文件
                    if not os.path.exists(temp_path):
                        # 下载PDF文件
                        logger.info(f"开始下载PDF: {url}")
                        response = requests.get(url)
                        response.raise_for_status()

                        with open(temp_path, "wb") as f:
                            f.write(response.content)
                        logger.info("PDF下载完成")

                    # 转换PDF文件
                    result = self.convert(temp_path)
                    logger.info("PDF转换完成")

                    # 处理文本内容
                    text_content = result["text_content"]
                    if "References" in text_content:
                        text_content = text_content.split("References")[0]
                    text_content = "\n".join(
                        [line for line in text_content.split("\n") if line.strip()]
                    )

                    # 更新结果
                    result["text_content"] = text_content
                    result["metadata"]["url"] = url
                    if description:
                        result["metadata"]["description"] = description
                    return result

                else:
                    # 获取网页内容
                    response = requests.get(url)
                    response.raise_for_status()

                    # 使用MarkItDown转换HTML
                    result = response.text

                    # 构建返回结果
                    metadata = {"title": url.split("/")[-1], "url": url, "file_type": "html"}

                    return {"text_content": result, "metadata": metadata, "images": []}

            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count < self.max_requests:
                    wait_time = 2**retry_count  # 指数退避
                    logger.warning(
                        f"网络错误: {str(e)}, 正在进行第 {retry_count}/{self.max_requests} 次重试, 等待 {wait_time} 秒..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"下载失败，已重试 {self.max_requests} 次: {str(e)}")
                    raise Exception(f"URL转换失败: {str(e)}")
            except Exception as e:
                raise Exception(f"URL转换失败: {str(e)}")
