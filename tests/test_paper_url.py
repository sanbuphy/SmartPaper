import os
import sys
import yaml
from typing import Dict
from pprint import pprint

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.reader import SmartPaper
from src.prompts.prompt_library import list_prompts

def load_config(config_path: str = "config/config.yaml") -> Dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_url_prompt(paper_url: str, prompt_name: str = None):
    """测试URL论文的提示词模式

    Args:
        paper_url (str): 论文URL
        prompt_name (str, optional): 提示词名称
    """
    config = load_config()
    reader = SmartPaper(output_format='markdown')
    
    print(f"\n{'='*50}")
    print(f"测试URL论文提示词模式: {prompt_name or '默认提示词'}")
    print(f"论文URL: {paper_url}")
    print(f"{'='*50}\n")
    
    result = reader.process_paper_url(paper_url, mode='prompt', prompt_name=prompt_name)
    print("分析结果:")
    print("-" * 50)
    print(result['result'])
    print("\n")

def test_url_agent(paper_url: str):
    """测试URL论文的Agent模式

    Args:
        paper_url (str): 论文URL
    """
    config = load_config()
    reader = SmartPaper(output_format='markdown')
    
    print(f"\n{'='*50}")
    print(f"测试URL论文Agent模式")
    print(f"论文URL: {paper_url}")
    print(f"{'='*50}\n")
    
    result = reader.process_paper_url(paper_url, mode='agent')
    
    print("结构化分析结果:")
    print("-" * 50)
    if 'structured_analysis' in result:
        for section, content in result['structured_analysis'].items():
            print(f"\n## {section.capitalize()}")
            print(content)
    else:
        print(result['result'])
    print("\n")

def main():
    """主测试函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法:")
        print("1. 测试URL提示词模式: python test_paper_url.py prompt <paper_url> [prompt_name]")
        print("2. 测试URL Agent模式: python test_paper_url.py agent <paper_url>")
        print("\n可用的提示词:")
        for name, desc in list_prompts().items():
            print(f"- {name}: {desc}")
        return

    mode = sys.argv[1]
    paper_url = sys.argv[2]

    if mode == 'prompt':
        prompt_name = sys.argv[3] if len(sys.argv) > 3 else None
        test_url_prompt(paper_url, prompt_name)
    elif mode == 'agent':
        test_url_agent(paper_url)
    else:
        print(f"错误: 未知的测试模式 - {mode}")

if __name__ == "__main__":
    main() 