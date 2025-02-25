"""
此测试文件用于测试本地PDF论文文件的处理功能。它提供了一个测试框架，可以使用不同的模式（agent模式或prompt模式）来分析单个PDF论文文件，并将分析结果保存为markdown格式。

示例用法：
    test_single_paper("path/to/paper.pdf", mode="agent")  # 使用agent模式分析论文
    test_single_paper("path/to/paper.pdf", mode="prompt", prompt_name="coolpapers")  # 使用特定提示词分析论文
"""

import os
import sys
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.reader import SmartPaper
from src.core.prompt_library import list_prompts


def test_single_paper(paper_path: str, mode: str = "agent", prompt_name: str = None):
    """测试单个本地PDF文件

    Args:
        paper_path (str): PDF文件路径
        mode (str): 分析模式 ('agent' 或 'prompt')
        prompt_name (str, optional): 提示词名称
    """
    reader = SmartPaper(output_format="markdown")

    print(f"\n{'='*50}")
    print(f"测试模式: {mode}")
    if mode == "prompt":
        print(f"提示词: {prompt_name or '默认提示词'}")
    print(f"论文路径: {paper_path}")
    print(f"{'='*50}\n")

    result = reader.process_paper(paper_path, mode=mode, prompt_name=prompt_name)

    # 生成输出文件名
    filename = os.path.splitext(os.path.basename(paper_path))[0]
    output_name = f"{filename}_{mode}"
    if mode == "prompt" and prompt_name:
        output_name += f"_{prompt_name}"

    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, "outputs", f"{output_name}.md")

    # 确保outputs目录存在
    os.makedirs(os.path.join(project_root, "outputs"), exist_ok=True)

    # 保存结果到文件
    with open(output_path, "w", encoding="utf-8") as f:
        if "structured_analysis" in result:
            for section, content in result["structured_analysis"].items():
                f.write(f"\n## {section.capitalize()}\n")
                f.write(content + "\n")
        else:
            f.write(result["result"])

    print(f"结果已保存到: {output_path}")
    print("\n分析结果:")
    print("-" * 50)
    if "structured_analysis" in result:
        for section, content in result["structured_analysis"].items():
            print(f"\n## {section.capitalize()}")
            print(content)
    else:
        print(result["result"])
    print("\n")


if __name__ == "__main__":
    # 测试配置
    TEST_PAPERS = {
        "single_paper": "../temp/2024.emnlp-main.54.pdf",  # 替换为实际的PDF文件路径
    }

    # 测试单个论文
    print("\n=== 测试单个论文 ===")

    # 不同提示词测试
    prompts_to_test = ["coolpapaers"]
    for prompt in prompts_to_test:
        print(f"\n--- {prompt}提示词测试 ---")
        test_single_paper(TEST_PAPERS["single_paper"], mode="prompt", prompt_name=prompt)
