import os
import sys
from typing import Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.reader import SmartPaper
from src.prompts.prompt_library import list_prompts

def test_url(url: str, mode: str = 'agent', prompt_name: str = None):
    """测试单个URL论文

    Args:
        url (str): 论文URL
        mode (str): 分析模式 ('agent' 或 'prompt')
        prompt_name (str, optional): 提示词名称
    """
    reader = SmartPaper(output_format='markdown')
    
    print(f"\n{'='*50}")
    print(f"测试模式: {mode}")
    if mode == 'prompt':
        print(f"提示词: {prompt_name or '默认提示词'}")
    print(f"论文URL: {url}")
    print(f"{'='*50}\n")
    
    result = reader.process_paper_url(url, mode=mode, prompt_name=prompt_name)
    
    # 创建outputs目录(如果不存在)
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存分析结果到outputs目录
    output_path = os.path.join(output_dir, f'analysis_{mode}_{prompt_name or "default"}.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        if 'structured_analysis' in result:
            for section, content in result['structured_analysis'].items():
                f.write(f"\n## {section.capitalize()}\n")
                f.write(f"{content}\n")
        else:
            f.write(result['result'])
    
    print("分析结果:")
    print("-" * 50)
    if 'structured_analysis' in result:
        for section, content in result['structured_analysis'].items():
            print(f"\n## {section.capitalize()}")
            print(content)
    else:
        print(result['result'])
    print(f"\n分析结果已保存到: {output_path}\n")

if __name__ == "__main__":
    # 测试配置
    print(list_prompts())

    TEST_PAPERS = [
        {
            "url": "https://arxiv.org/pdf/2305.12002",  # 替换为实际的论文URL
            "description": "GPT-4论文"
        },
        # 可以添加更多测试论文
    ]
    
    # # 运行Agent模式测试
    # print("\n=== 运行Agent模式测试 ===")
    # test_url(TEST_PAPERS[0]["url"], mode='agent')
    
    # 运行不同提示词的测试
    prompts_to_test = ['yuanbao']
    for prompt in prompts_to_test:
        print(f"\n=== 运行{prompt}提示词测试 ===")
        test_url(TEST_PAPERS[0]["url"], mode='prompt', prompt_name=prompt)