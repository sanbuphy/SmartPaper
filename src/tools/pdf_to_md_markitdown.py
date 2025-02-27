"""
#### 修改说明：
1. 移除对`markdown-it-py`库的错误使用
2. 使用`pdfplumber`进行PDF文本提取
3. 添加HTML转Markdown功能
4. 完善文件类型处理逻辑
"""

import os
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import requests
import mimetypes
import pdfplumber
from loguru import logger
import time
import html2text  # 新增HTML转Markdown库

class MarkdownConverter:
    """通用文档转Markdown转换器"""

    def __init__(self, llm_client: Any = None, llm_model: str = None, config: Dict = None):
        """
        Args:
            llm_client (any): 用于高级功能的LLM客户端
            llm_model (str): LLM模型名称
            config (Dict, optional): 配置信息
        """
        # 初始化配置
        self.config = config or {}
        self.max_requests = self.config.get("llm", {}).get("max_requests", 3)
        self.llm_client = llm_client
        self.llm_model = llm_model

        # 初始化HTML转换器
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False

        # 支持的文件类型
        self.supported_extensions = {
            ".pdf": self._convert_pdf,
            ".docx": self._convert_docx,
            ".html": self._convert_html,
            ".txt": self._convert_text,
            ".md": self._convert_text,
        }

        logger.info("MarkdownConverter初始化完成")

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
            # 调用对应的转换方法
            return self.supported_extensions[ext](file_path)
        except Exception as e:
            raise Exception(f"文件转换失败: {str(e)}")

    def convert_url(self, url: str, description: str = None) -> Dict:
        """下载并转换URL文件
        
        Args:
            url (str): 文件URL
            description (str, optional): 论文描述
            
        Returns:
            Dict: 包含转换结果的字典
        """
        for retry in range(self.max_requests):
            try:
                # 处理arxiv的特殊情况
                if "arxiv.org" in url.lower():
                    return self._process_arxiv(url, description)
                
                # 通用URL处理
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # 获取内容类型
                content_type = response.headers.get('Content-Type', '').split(';')[0]
                
                # 根据类型处理内容
                if content_type == 'application/pdf':
                    return self._process_pdf_from_url(url, response.content)
                elif 'text/html' in content_type:
                    return self._process_html(url, response.text)
                else:
                    return self._process_unknown_type(url, response.content)
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 ({retry+1}/{self.max_requests}): {str(e)}")
                time.sleep(2 ** retry)  # 指数退避
        raise Exception(f"无法下载文件: {url}")

    # region 私有方法 ------------------------------------------------------------
    def _convert_pdf(self, file_path: Path) -> Dict:
        """处理PDF文件转换"""
        text_content = []
        metadata = {}
        
        with pdfplumber.open(file_path) as pdf:
            # 提取元数据
            if pdf.metadata:
                metadata.update({
                    "title": pdf.metadata.get("Title", ""),
                    "author": pdf.metadata.get("Author", ""),
                    "creation_date": pdf.metadata.get("CreationDate", "")
                })
            
            # 提取文本
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        return {
            "text_content": self._format_as_markdown("\n".join(text_content)),
            "metadata": metadata,
            "images": []  # 需要添加图片处理逻辑
        }

    def _convert_html(self, file_path: Path) -> Dict:
        """处理HTML文件转换"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return self._process_html(str(file_path), html_content)

    def _convert_docx(self, file_path: Path) -> Dict:
        """处理DOCX文件转换（需实现）"""
        # 这里需要添加实际的DOCX转换逻辑
        return {
            "text_content": f"# DOCX文件内容\n\n{file_path.name}（DOCX转换功能待实现）",
            "metadata": {"source": str(file_path)},
            "images": []
        }

    def _convert_text(self, file_path: Path) -> Dict:
        """处理纯文本文件转换"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "text_content": self._format_as_markdown(content),
            "metadata": {"source": str(file_path)},
            "images": []
        }

    def _format_as_markdown(self, text: str) -> str:
        """将纯文本格式化为Markdown"""
        # 添加基础格式化规则
        formatted = []
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # 检测标题
            if line.isupper() and len(line) < 100:
                formatted.append(f"## {line}")
            else:
                formatted.append(line)
        return "\n\n".join(formatted)

    def _process_arxiv(self, url: str, description: str) -> Dict:
        """处理arXiv的特殊情况"""
        temp_dir = Path(tempfile.gettempdir()) / "arxiv_papers"
        temp_dir.mkdir(exist_ok=True)
        
        arxiv_id = re.search(r"\d+\.\d+", url)
        if not arxiv_id:
            raise ValueError("无效的arXiv URL")
            
        file_path = temp_dir / f"{arxiv_id.group()}.pdf"
        
        # 下载PDF（如果尚未缓存）
        if not file_path.exists():
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(response.content)
                
        # 转换PDF
        result = self.convert(str(file_path))
        
        # 后处理
        if "References" in result["text_content"]:
            result["text_content"] = result["text_content"].split("References")[0]
            
        result["metadata"].update({
            "url": url,
            "description": description or "",
            "source": "arxiv"
        })
        return result

    def _process_html(self, url: str, html: str) -> Dict:
        """处理HTML内容转换"""
        markdown = self.html_converter.handle(html)
        return {
            "text_content": markdown,
            "metadata": {
                "title": self._extract_html_title(html),
                "url": url,
                "source_type": "webpage"
            },
            "images": []  # 需要添加图片提取逻辑
        }

    def _extract_html_title(self, html: str) -> str:
        """从HTML中提取标题"""
        match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
        return match.group(1).strip() if match else "Untitled"

    def _process_pdf_from_url(self, url: str, content: bytes) -> Dict:
        """处理来自URL的PDF"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
            
        result = self.convert(str(tmp_path))
        tmp_path.unlink()  # 删除临时文件
        
        result["metadata"]["url"] = url
        return result

    def _process_unknown_type(self, url: str, content: bytes) -> Dict:
        """处理未知文件类型"""
        return {
            "text_content": f"# 无法转换的文件类型\n\nURL: {url}",
            "metadata": {"url": url, "warning": "unsupported_type"},
            "images": []
        }
    # endregion ------------------------------------------------------------------
