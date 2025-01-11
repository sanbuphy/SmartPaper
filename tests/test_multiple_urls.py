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
    
    # 创建outputs目录(如果不存在)
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    total_papers = len(urls)
    for i, paper in enumerate(urls, 1):
        print(f"\n当前分析第 {i}/{total_papers} 篇论文")
        print(f"进度: [{'='*int(20*i/total_papers)}{' '*(20-int(20*i/total_papers))}] {int(100*i/total_papers)}%")
        print(f"\n--- 处理论文: {paper['description']} ---")
        print(f"URL: {paper['url']}\n")
        
        # 生成文件名(取description前8个单词)
        description_words = paper['description'].split()[:8]
        filename = '_'.join(description_words)
        output_path = os.path.join(output_dir, f'{filename}_{mode}_{prompt_name or "default"}.md')
        
        # 检查文件是否已存在
        if os.path.exists(output_path):
            print(f"文件已存在,跳过: {output_path}\n")
            continue
            
        result = reader.process_paper_url(paper['url'], mode=mode, prompt_name=prompt_name, description=paper['description'])
        
        # 保存分析结果
        with open(output_path, 'w', encoding='utf-8') as f:
            # 直接写入完整的格式化结果
            f.write(result['result'])
        
        print("分析结果:")
        print("-" * 30)
        print(result['result'])
        print(f"\n分析结果已保存到: {output_path}\n")

if __name__ == "__main__":
    # 测试配置
    TEST_PAPERS = [
        {
            "url": "https://arxiv.org/pdf/2203.14465.pdf",
            "description": "STaR: Bootstrapping Reasoning With Reasoning (NeurIPS 2022)"
        },
        {
            "url": "https://arxiv.org/pdf/2110.07178.pdf", 
            "description": "Symbolic Knowledge Distillation: from General Language Models to Commonsense Models (NAACL 2022)"
        },
        {
            "url": "https://arxiv.org/pdf/2202.04538.pdf",
            "description": "Generating Training Data with Language Models: Towards Zero-Shot Language Understanding (NeurIPS 2022)"
        },
        {
            "url": "https://arxiv.org/pdf/2202.07922.pdf",
            "description": "ZeroGen: Efficient Zero-shot Learning via Dataset Generation (EMNLP 2022)"
        },
        {
            "url": "https://arxiv.org/pdf/2303.17760.pdf",
            "description": "CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society (NeurIPS 2023)"
        },
        {
            "url": "https://arxiv.org/pdf/2401.01335.pdf",
            "description": "Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models (ICML 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2401.10020.pdf",
            "description": "Self-Rewarding Language Models (Arxiv 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2402.13064.pdf",
            "description": "Synthetic Data (Almost) from Scratch: Generalized Instruction Tuning for Language Models (Arxiv 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2212.10560.pdf",
            "description": "Self-instruct: Aligning language models with self-generated instructions (ACL 2023)"
        },
        {
            "url": "https://arxiv.org/pdf/2401.16380.pdf",
            "description": "Rephrasing the Web: A Recipe for Compute and Data-Efficient Language Modeling (ACL 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2310.17876.pdf",
            "description": "TarGEN: Targeted Data Generation with Large Language Models (COLM 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2406.00770.pdf", 
            "description": "Automatic Instruction Evolving for Large Language Models (Arxiv 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2406.20094",
            "description": "Scaling Synthetic Data Creation with 1,000,000,000 Personas (Arxiv 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2404.10642",
            "description": "Self-playing Adversarial Language Game Enhances LLM Reasoning (Arxiv 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2409.08239",
            "description": "Source2Synth: Synthetic Data Generation and Curation Grounded in Real Data Sources (Arxiv 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2402.18334",
            "description": "Learning to Generate Instruction Tuning Datasets for Zero-Shot Task Adaptation (ACL Findings 2024)"
        },
        {
            "url": "https://arxiv.org/pdf/2406.08464",
            "description": "Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing (Arxiv 2024)"
        }
        
    ]
    
    # # 使用Agent模式测试所有论文
    # print("\n=== Agent模式批量测试 ===")
    # test_urls(TEST_PAPERS, mode='agent')
    
    # 使用summary提示词测试所有论文
    print("\n=== Summary提示词批量测试 ===")
    test_urls(TEST_PAPERS, mode='prompt', prompt_name='yuanbao') 