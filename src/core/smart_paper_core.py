import os
from typing import Dict, List, Optional, Generator
import yaml
from pathlib import Path
import requests

from core.llm_wrapper import LLMWrapper
from core.document_converter import convert_to_text
from utils.output_formatter import OutputFormatter
from loguru import logger


class SmartPaper:
    """论文阅读和存档工具"""

    def __init__(self, config_file: Optional[str] = None, output_format: str = "markdown"):
        """初始化SmartPaper实例

        Args:
            config_file (Optional[str], optional): 配置文件路径
            output_format (str, optional): 输出格式 (markdown/csv/folder)
        """
        # 加载配置
        if config_file is None:
            config_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "config.yaml"
            )

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        self.config = self._load_config(config_file)
        logger.info(f"加载配置文件成功: {config_file}")

        # 初始化组件
        self.processor: LLMWrapper = LLMWrapper(self.config)
        self.output_formatter: OutputFormatter = OutputFormatter(self.config["output"])
        logger.info("初始化组件完成")

        # 设置输出格式
        self.output_format = output_format

    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件

        Args:
            config_file (str): 配置文件路径

        Returns:
            Dict: 配置信息
        """
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"加载配置文件失败: {str(e)}")

    def process_paper(self, file_path: str, prompt_name: Optional[str] = None) -> Dict:
        """处理单个论文文件

        Args:
            file_path (str): 论文文件路径
            prompt_name (Optional[str], optional): 提示词名称

        Returns:
            Dict: 处理结果
        """
        try:
            # 转换PDF，使用配置中指定的转换器
            converter_name = self.config.get("document_converter", {}).get(
                "converter_name", "markitdown"
            )
            result = convert_to_text(file_path, config=self.config, converter_name=converter_name)
            logger.info(f"转换PDF成功: {file_path}，使用转换器: {converter_name}")

            # 使用提示词模式处理
            analysis = self.processor.process_with_content(result["text_content"], prompt_name)

            # 格式化输出
            output = self.output_formatter.format(
                content=analysis, metadata=result["metadata"], format=self.output_format
            )

            return output

        except Exception as e:
            raise Exception(f"处理论文失败: {str(e)}")

    def process_directory(self, dir_path: str, prompt_name: Optional[str] = None) -> List[Dict]:
        """处理目录中的所有论文

        Args:
            dir_path (str): 目录路径
            prompt_name (Optional[str], optional): 提示词名称

        Returns:
            List[Dict]: 处理结果列表
        """
        results = []
        dir_path = Path(dir_path)

        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")

        for file_path in dir_path.glob("*.pdf"):
            try:
                result = self.process_paper(str(file_path), prompt_name)
                results.append(result)
            except Exception as e:
                logger.error(f"处理文件 {file_path} 失败: {str(e)}")

        return results

    def convert_url(self, url: str, description: Optional[str] = None) -> Dict:
        """从URL下载并转换文件

        Args:
            url (str): 文件URL
            description (str, optional): 文件描述

        Returns:
            Dict: 包含转换结果的字典
        """
        try:
            # 获取配置中指定的转换器
            converter_name = self.config.get("document_converter", {}).get(
                "converter_name", "markitdown"
            )

            # 判断是否为PDF文件
            is_arxiv = "arxiv.org" in url.lower()

            if is_arxiv:
                # 创建temp目录用于处理当前请求
                temp_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp"
                )
                os.makedirs(temp_dir, exist_ok=True)

                # 从URL提取文件名
                arxiv_id = url.split("/")[-1]
                if not arxiv_id.endswith(".pdf"):
                    arxiv_id += ".pdf"
                temp_path = os.path.join(temp_dir, arxiv_id)

                # 下载PDF文件
                logger.info(f"开始下载PDF: {url}")
                try:
                    response = requests.get(url, timeout=30)  # 设置超时
                    response.raise_for_status()

                    # 保存到临时目录
                    with open(temp_path, "wb") as f:
                        f.write(response.content)
                    logger.info("PDF下载完成")
                except Exception as e:
                    raise Exception(f"下载PDF失败: {str(e)}")

                # 转换PDF文件
                result = convert_to_text(
                    temp_path, config=self.config, converter_name=converter_name
                )
                logger.info(f"PDF转换完成，使用转换器: {converter_name}")

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
                # 创建temp目录用于处理当前请求
                temp_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp"
                )
                os.makedirs(temp_dir, exist_ok=True)

                # 获取网页内容
                response = requests.get(url)
                response.raise_for_status()

                # 确定文件名和路径
                file_suffix = ".html"  # 假设默认为html，可以根据content-type改进
                temp_path = os.path.join(temp_dir, f"downloaded_content{file_suffix}")

                # 保存内容到临时文件
                with open(temp_path, "wb") as temp_file:
                    temp_file.write(response.content)

                # 转换HTML文件
                result = convert_to_text(
                    temp_path, config=self.config, converter_name=converter_name
                )
                logger.info(f"HTML转换完成，使用转换器: {converter_name}")

                # 添加元数据
                metadata = {"title": url.split("/")[-1], "url": url, "file_type": "html"}
                result["metadata"] = {**result.get("metadata", {}), **metadata}

                return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"下载文件失败: {str(e)}")
        except Exception as e:
            raise Exception(f"URL转换失败: {str(e)}")

    def process_paper_url(
        self,
        url: str,
        prompt_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """处理论文URL

        Args:
            url (str): 论文URL
            prompt_name (Optional[str], optional): 提示词名称
            description (Optional[str], optional): 论文描述

        Returns:
            Dict: 处理结果
        """
        try:
            # 下载并转换PDF
            logger.info(f"开始处理论文URL: {url}")
            result = self.convert_url(url, description=description)
            logger.info("PDF转换完成，开始分析")

            # 获取PDF内容
            text_content = result["text_content"]
            metadata = result["metadata"]

            # 使用提示词模式处理
            analysis = self.processor.process_with_content(text_content, prompt_name)
            logger.info(f"分析完成")

            # 格式化输出
            output = self.output_formatter.format(
                content=analysis, metadata=metadata, format=self.output_format
            )

            return output

        except Exception as e:
            raise Exception(f"处理论文URL失败: {str(e)}")

    def process_paper_url_stream(
        self,
        url: str,
        prompt_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """流式处理论文URL

        Args:
            url (str): 论文URL
            prompt_name (str, optional): 提示词名称
            description (str, optional): 论文描述

        Yields:
            str: 流式输出的文本片段

        Raises:
            Exception: 当处理失败时抛出异常
        """
        try:
            # 打印 metainfo 信息
            yield "✨ 元数据信息 ✨\n\n"
            yield f"📄 处理URL: {url}\n\n"
            yield f"💡 提示词模板: {prompt_name if prompt_name else '默认'}\n\n"
            yield f"📝 描述信息: {description if description else '无'}\n\n"
            # 下载并转换PDF
            logger.info(f"开始流式处理论文URL: {url}")
            yield "🚀 正在下载并转换PDF...\n\n"

            result = self.convert_url(url, description=description)
            logger.info("PDF转换完成，开始流式分析")
            yield "✅ PDF转换完成，开始分析...\n\n"

            # 获取PDF内容
            text_content = result["text_content"]

            # 使用提示词模式处理
            yield "使用提示词模式进行分析...\n"
            # 使用流式接口处理
            for chunk in self.processor.process_stream_with_content(text_content, prompt_name):
                yield chunk

            logger.info(f"流式分析完成")

        except Exception as e:
            error_msg = f"流式处理论文URL失败: {str(e)}"
            logger.error(error_msg)
            yield f"错误: {error_msg}"
            raise Exception(error_msg)

    def set_api_key(self, api_key: str):
        """设置API密钥

        Args:
            api_key (str): API密钥
        """
        self.processor.set_api_key(api_key)

    def reset_request_count(self):
        """重置所有组件的请求计数器"""
        self.processor.reset_request_count()
