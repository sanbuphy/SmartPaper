"""
此测试文件用于批量测试多个URL论文的分析功能。它可以同时处理多篇论文并显示进度条。每篇论文可以提供描述信息，分析结果会以markdown格式保存到outputs目录，文件名会包含论文描述的关键词。该文件还实现了断点续传功能，如果某篇论文的分析结果已存在，会自动跳过。

示例用法：
    papers = [
        {"url": "https://arxiv.org/pdf/2203.14465.pdf", "description": "STaR: Bootstrapping Reasoning"},
        {"url": "https://arxiv.org/pdf/2305.12002.pdf", "description": "GPT-4 Technical Report"}
    ]
    test_urls(papers, prompt_name="yuanbao")  # 使用特定提示词批量分析论文
"""

import os
import sys
from typing import Dict, List
from loguru import logger
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.smart_paper_core import SmartPaper


def test_urls(urls: List[Dict], prompt_name: str = None):
    """测试多个URL论文

    Args:
        urls (List[Dict]): 论文URL列表，每个元素包含url和description
        prompt_name (str, optional): 提示词名称
    """
    reader = SmartPaper(output_format="markdown")

    logger.info(f"提示词: {prompt_name or '默认提示词'}")

    # 创建outputs目录(如果不存在)
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"
    )
    os.makedirs(output_dir, exist_ok=True)

    total_papers = len(urls)
    for i, paper in enumerate(urls, 1):
        logger.info(f"\n当前分析第 {i}/{total_papers} 篇论文")
        logger.info(
            f"进度: [{'='*int(20*i/total_papers)}{' '*(20-int(20*i/total_papers))}] {int(100*i/total_papers)}%"
        )
        logger.info(f"\n--- 处理论文: {paper['description']} ---")
        logger.info(f"URL: {paper['url']}\n")

        # 生成文件名(取description前8个单词)
        description_words = re.sub(r"[^\w\s-：]", "_", paper["description"]).split()[:8]
        filename = "_".join(description_words)
        output_path = os.path.join(output_dir, f'{filename}_{prompt_name or "default"}.md')

        # 检查文件是否已存在
        if os.path.exists(output_path):
            logger.info(f"文件已存在,跳过: {output_path}\n")
            continue

        result = reader.process_paper_url(
            paper["url"], prompt_name=prompt_name, description=paper["description"]
        )

        # 保存分析结果
        with open(output_path, "w", encoding="utf-8") as f:
            # 直接写入完整的格式化结果
            f.write(result["result"])

        logger.info("分析结果:")
        logger.info("-" * 30)
        logger.info(result["result"])
        logger.info(f"\n分析结果已保存到: {output_path}\n")


if __name__ == "__main__":
    # 测试配置
    TEST_PAPERS = [
        {
            "url": "https://arxiv.org/pdf/2203.14465.pdf",
            "description": "STaR: Bootstrapping Reasoning With Reasoning (NeurIPS 2022)",
        },
    ]

    # 使用指定提示词测试所有论文
    logger.info("\n=== 使用提示词批量测试 ===")
    test_urls(TEST_PAPERS, prompt_name="yuanbao")
