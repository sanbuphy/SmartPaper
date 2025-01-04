import os
import sys
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.reader import SmartPaper
from src.prompts.prompt_library import list_prompts

def test_urls(urls: List[Dict], mode: str = 'agent', prompt_name: str = None):
    """测试多个URL论文

    Args:
        urls (List[Dict]): 论文URL列表，每个元素包含url和description
        mode (str): 分析模式 ('agent' 或 'prompt')
        prompt_name (str, optional): 提示词名称
    """
    reader = SmartPaper(output_format='markdown')
    
    print(f"\n{'='*50}")
    print(f"批量测试模式: {mode}")
    if mode == 'prompt':
        print(f"提示词: {prompt_name or '默认提示词'}")
    print(f"{'='*50}\n")
    
    for paper in urls:
        print(f"\n--- 处理论文: {paper['description']} ---")
        print(f"URL: {paper['url']}\n")
        
        result = reader.process_paper_url(paper['url'], mode=mode, prompt_name=prompt_name)
        
        print("分析结果:")
        print("-" * 30)
        if 'structured_analysis' in result:
            for section, content in result['structured_analysis'].items():
                print(f"\n## {section.capitalize()}")
                print(content)
        else:
            print(result['result'])
        print("\n")

if __name__ == "__main__":
    # 测试配置
    TEST_PAPERS = [
        {
            "url": "https://arxiv.org/pdf/2312.12456.pdf",  # 替换为实际的论文URL
            "description": "GPT-4论文"
        },
        {
            "url": "https://arxiv.org/pdf/2312.11805.pdf",  # 替换为实际的论文URL
            "description": "LLM综述论文"
        },
        {
            "url": "https://arxiv.org/pdf/2312.00752.pdf",  # 替换为实际的论文URL
            "description": "AI Agent论文"
        }
    ]
    
    # 使用Agent模式测试所有论文
    print("\n=== Agent模式批量测试 ===")
    test_urls(TEST_PAPERS, mode='agent')
    
    # 使用summary提示词测试所有论文
    print("\n=== Summary提示词批量测试 ===")
    test_urls(TEST_PAPERS, mode='prompt', prompt_name='summary') 