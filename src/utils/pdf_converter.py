import os
from typing import Dict, Optional, Any
from pathlib import Path
import tempfile
import requests
from tools.everything_to_text.pdf_to_md_markitdown import MarkdownConverter


class PDFConverter:
    """PDF文档转换器"""

    def __init__(
        self, config: Optional[Dict] = None, llm_client: Any = None, llm_model: str = None
    ):
        """初始化转换器

        Args:
            config (Optional[Dict]): 配置信息
            llm_client (Any): LLM客户端,用于图像描述等高级功能
            llm_model (str): LLM模型名称
        """
        self.converter = MarkdownConverter(
            config=config, llm_client=llm_client, llm_model=llm_model
        )

    def convert(self, file_path: str) -> Dict:
        """转换PDF文件为文本

        Args:
            file_path (str): PDF文件路径

        Returns:
            Dict: 包含转换结果的字典
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if file_path.suffix.lower() != ".pdf":
            raise ValueError("仅支持PDF文件")

        return self.converter.convert(str(file_path))

    def convert_url(self, url: str) -> Dict | None:
        """从URL下载并转换PDF文件

        Args:
            url (str): PDF文件URL

        Returns:
            Dict: 包含转换结果的字典
        """
        try:
            # 下载文件
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # 检查内容类型
            content_type = response.headers.get("content-type", "")
            if "application/pdf" not in content_type.lower():
                raise ValueError("URL必须指向PDF文件")

            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                temp_path = temp_file.name

            # 转换文件
            try:
                result = self.convert(temp_path)
                result["url"] = url
                return result
            finally:
                # 清理临时文件
                os.unlink(temp_path)

        except Exception as e:
            raise Exception(f"URL文件转换失败: {str(e)}")
