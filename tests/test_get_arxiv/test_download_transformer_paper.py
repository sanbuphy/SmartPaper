#!/usr/bin/env python
"""
示例脚本：下载 Transformer 经典论文 'Attention Is All You Need'

这个脚本展示了如何使用 SmartPaper 的 get_arxiv 模块来:
1. 搜索关于 Transformer 的论文
2. 获取特定论文的元数据
3. 下载论文的 PDF 文件
"""

import os
import logging
from pathlib import Path
import sys


# 上一级目录是tests，再上一级目录是SmartPaper
# 这段代码的作用是将当前文件所在目录的上两级目录添加到Python的模块搜索路径中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SmartPaper.get_arxiv import ArxivClient, download_paper

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    # 创建下载目录
    download_dir = Path("../test_datas/test_arxiv_downloads")
    download_dir.mkdir(exist_ok=True)
    
    # 创建 ArxivClient 实例
    client = ArxivClient()
    
    print("\n===== 1. 搜索 Transformer 相关论文 =====")
    # 搜索相关论文
    papers = client.search("transformer attention neural networks", max_results=5)
    
    # 打印搜索结果
    for i, paper in enumerate(papers, 1):
        print(f"\n论文 {i}:")
        print(f"ID: {paper.paper_id}")
        print(f"标题: {paper.title}")
        print(f"作者: {', '.join(paper.authors)}")
        print(f"发布日期: {paper.published.strftime('%Y-%m-%d')}")
        print(f"摘要: {paper.abstract[:150]}...")
    
    print("\n\n===== 2. 获取 Transformer 原始论文 'Attention Is All You Need' =====")
    # Transformer 经典论文的 ID
    transformer_paper_id = "1706.03762"
    
    # 获取论文元数据
    transformer_paper = client.get_by_id(transformer_paper_id)
    
    # 打印论文详细信息
    print(f"标题: {transformer_paper.title}")
    print(f"作者: {', '.join(transformer_paper.authors)}")
    print(f"发布日期: {transformer_paper.published.strftime('%Y-%m-%d')}")
    print(f"分类: {', '.join(transformer_paper.categories)}")
    print(f"主分类: {transformer_paper.primary_category}")
    print(f"PDF URL: {transformer_paper.pdf_url}")
    print(f"网页 URL: {transformer_paper.web_url}")
    if transformer_paper.doi:
        print(f"DOI: {transformer_paper.doi}")
    if transformer_paper.comment:
        print(f"评论: {transformer_paper.comment}")
    print(f"\n摘要:\n{transformer_paper.abstract}")
    
    print("\n\n===== 3. 下载 Transformer 论文 =====")
    # 下载论文
    pdf_path, metadata = download_paper(
        transformer_paper_id,
        download_dir,
        filename="Attention_Is_All_You_Need.pdf",
        get_metadata=True
    )
    
    print(f"论文已下载至: {pdf_path}")
    print(f"文件大小: {os.path.getsize(pdf_path) / 1024:.2f} KB")
    
    print("\n===== 完成! =====")

if __name__ == "__main__":
    main()