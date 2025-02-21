import os
import csv
import json
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd


class OutputFormatter:
    """输出格式化工具"""

    def __init__(self, config: Dict[str, Any]):
        """初始化输出格式化工具

        Args:
            config (Dict[str, Any]): 输出配置
        """
        self.config = config
        self.base_path = config["base_path"]
        os.makedirs(self.base_path, exist_ok=True)

    def format(self, content: Dict, metadata: Dict, format: str = "markdown") -> Dict:
        """格式化输出内容

        Args:
            content (Dict): 分析内容
            metadata (Dict): 元数据
            format (str): 输出格式 (markdown/csv/folder)

        Returns:
            Dict: 格式化后的内容
        """
        # 添加时间戳
        timestamp = datetime.now().isoformat()

        if format == "markdown":
            return self._format_markdown(content, metadata, timestamp)
        elif format == "csv":
            return self._format_csv(content, metadata, timestamp)
        elif format == "folder":
            return self._format_folder(content, metadata, timestamp)
        else:
            raise ValueError(f"不支持的输出格式: {format}")

    def _format_markdown(self, content: Dict, metadata: Dict, timestamp: str) -> Dict:
        """格式化为Markdown格式

        Args:
            content (Dict): 分析内容
            metadata (Dict): 元数据
            timestamp (str): 时间戳

        Returns:
            Dict: 格式化后的内容
        """
        # 构建Markdown内容
        markdown = []

        # 添加元数据
        markdown.append("# 论文分析报告\n")
        markdown.append("## 元数据")
        markdown.append(f"- 标题: {metadata.get('title', 'N/A')}")
        markdown.append(f"- 作者: {metadata.get('author', 'N/A')}")
        markdown.append(f"- 日期: {metadata.get('date', 'N/A')}")
        if "url" in metadata:
            markdown.append(f"- URL: {metadata['url']}")
        if "description" in metadata:
            markdown.append(f"- 描述: {metadata['description']}")
        markdown.append(f"- 分析时间: {timestamp}\n")

        # 添加分析内容
        markdown.append("## 分析结果")
        if "result" in content:
            markdown.append(content["result"])
        elif "structured_analysis" in content:
            for section, text in content["structured_analysis"].items():
                markdown.append(f"\n### {section.capitalize()}")
                markdown.append(text)

        return {"result": "\n".join(markdown), "metadata": metadata, "timestamp": timestamp}

    def _format_csv(self, content: Dict, metadata: Dict, timestamp: str) -> Dict:
        """格式化为CSV格式

        Args:
            content (Dict): 分析内容
            metadata (Dict): 元数据
            timestamp (str): 时间戳

        Returns:
            Dict: 格式化后的内容
        """
        # 准备CSV数据
        csv_data = {
            "title": metadata.get("title", ""),
            "url": metadata.get("url", ""),
            "author": metadata.get("author", ""),
            "date": metadata.get("date", ""),
            "timestamp": timestamp,
        }

        # 添加分析结果
        if "result" in content:
            csv_data["summary"] = content["result"]
        elif "structured_analysis" in content:
            for section, text in content["structured_analysis"].items():
                csv_data[section] = text

        return {"result": pd.DataFrame([csv_data]), "metadata": metadata, "timestamp": timestamp}

    def _format_folder(self, content: Dict, metadata: Dict, timestamp: str) -> Dict:
        """格式化为文件夹结构

        Args:
            content (Dict): 分析内容
            metadata (Dict): 元数据
            timestamp (str): 时间戳

        Returns:
            Dict: 格式化后的内容
        """
        # 创建结构化数据
        structured_data = {"metadata": metadata, "content": content, "timestamp": timestamp}

        return {
            "result": json.dumps(structured_data, ensure_ascii=False, indent=2),
            "metadata": metadata,
            "timestamp": timestamp,
        }
