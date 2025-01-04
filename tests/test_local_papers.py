import os
import sys
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.reader import SmartPaper
from src.prompts.prompt_library import list_prompts

def test_single_paper(paper_path: str, mode: str = 'agent', prompt_name: str = None):
    """测试单个本地PDF文件

    Args:
        paper_path (str): PDF文件路径
        mode (str): 分析模式 ('agent' 或 'prompt')
        prompt_name (str, optional): 提示词名称
    """
    reader = SmartPaper(output_format='markdown')
    
    print(f"\n{'='*50}")
    print(f"测试模式: {mode}")
    if mode == 'prompt':
        print(f"提示词: {prompt_name or '默认提示词'}")
    print(f"论文路径: {paper_path}")
    print(f"{'='*50}\n")
    
    result = reader.process_paper(paper_path, mode=mode, prompt_name=prompt_name)
    
    print("分析结果:")
    print("-" * 50)
    if 'structured_analysis' in result:
        for section, content in result['structured_analysis'].items():
            print(f"\n## {section.capitalize()}")
            print(content)
    else:
        print(result['result'])
    print("\n")

def test_paper_directory(directory: str, mode: str = 'agent', prompt_name: str = None):
    """测试文件夹中的所有PDF文件

    Args:
        directory (str): PDF文件目录
        mode (str): 分析模式 ('agent' 或 'prompt')
        prompt_name (str, optional): 提示词名称
    """
    reader = SmartPaper(output_format='markdown')
    
    print(f"\n{'='*50}")
    print(f"批量测试模式: {mode}")
    if mode == 'prompt':
        print(f"提示词: {prompt_name or '默认提示词'}")
    print(f"论文目录: {directory}")
    print(f"{'='*50}\n")
    
    results = reader.process_papers(directory, mode=mode, prompt_name=prompt_name)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- 论文 {i}: {result.get('file_path', 'Unknown')} ---\n")
        
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
    TEST_PAPERS = {
        "single_paper": "papers/example.pdf",  # 替换为实际的PDF文件路径
        "paper_directory": "papers/ai_papers"  # 替换为实际的PDF文件夹路径
    }
    
    # 测试单个论文
    print("\n=== 测试单个论文 ===")
    
    # Agent模式
    print("\n--- Agent模式测试 ---")
    test_single_paper(TEST_PAPERS["single_paper"], mode='agent')
    
    # 不同提示词测试
    prompts_to_test = ['summary', 'methodology', 'full_analysis']
    for prompt in prompts_to_test:
        print(f"\n--- {prompt}提示词测试 ---")
        test_single_paper(TEST_PAPERS["single_paper"], mode='prompt', prompt_name=prompt)
    
    # 测试文件夹
    print("\n=== 测试论文文件夹 ===")
    
    # Agent模式
    print("\n--- Agent模式批量测试 ---")
    test_paper_directory(TEST_PAPERS["paper_directory"], mode='agent')
    
    # Summary提示词测试
    print("\n--- Summary提示词批量测试 ---")
    test_paper_directory(TEST_PAPERS["paper_directory"], mode='prompt', prompt_name='summary') 