import os
import sys
from typing import Dict
from pprint import pprint

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.markdown_converter import MarkdownConverter
import requests

def test_arxiv_download():
    """测试从arxiv下载并转换论文"""
    
    # 创建临时文件夹
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(project_root, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # 下载PDF
    arxiv_url = "https://arxiv.org/pdf/1706.03762"
    pdf_path = os.path.join(temp_dir, "1706.03762.pdf")
    
    print(f"\n{'='*50}")
    print(f"开始下载论文")
    print(f"URL: {arxiv_url}")
    
    response = requests.get(arxiv_url)
    with open(pdf_path, "wb") as f:
        f.write(response.content)
    
    print(f"PDF已保存至: {pdf_path}")
    
    # 配置转换器
    converter = MarkdownConverter()
    
    print(f"\n开始转换PDF到Markdown")
    result = converter.convert(pdf_path)['text_content']
    
    # 只保留References之前的内容
    if "References" in result:
        result = result.split("References")[0]
    result = "\n".join([line for line in result.split("\n") if line.strip()])
    
    print("\n文件内容:")
    print("-" * 30)
    print(result)

if __name__ == "__main__":
    test_arxiv_download()
