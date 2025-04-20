"""
此测试文件用于测试本地PDF论文文件的处理功能。它提供了一个测试框架，可以使用提示词来分析单个PDF论文文件，并将分析结果保存为markdown格式。

示例用法：
    test_single_paper("path/to/paper.pdf")  # 使用默认提示词分析论文
    test_single_paper("path/to/paper.pdf", prompt_name="coolpapers")  # 使用特定提示词分析论文
"""

import os
import sys
from loguru import logger

# 添加项目根目录到Python路径

from core.smart_paper_core import SmartPaper


def test_single_paper(paper_path: str, prompt_name: str = None):
    """测试单个本地PDF文件

    Args:
        paper_path (str): PDF文件路径
        prompt_name (str, optional): 提示词名称
    """
    reader = SmartPaper(output_format="markdown")

    logger.info(f"提示词: {prompt_name or '默认提示词'}")
    logger.info(f"论文路径: {paper_path}")

    result = reader.process_paper(paper_path, prompt_name)

    # 生成输出文件名
    filename = os.path.splitext(os.path.basename(paper_path))[0]
    output_name = f"{filename}"
    if prompt_name:
        output_name += f"_{prompt_name}"

    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, "outputs", f"{output_name}.md")

    # 确保outputs目录存在
    os.makedirs(os.path.join(project_root, "outputs"), exist_ok=True)

    # 保存结果
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["result"])

    logger.info(f"分析结果已保存到: {output_path}")
    return result


if __name__ == "__main__":
    # 测试配置
    TEST_PAPERS = {
        "single_paper": "../temp/2024.emnlp-main.54.pdf",  # 替换为实际的PDF文件路径
    }

    # 测试单个论文
    logger.info("\n=== 测试单个论文 ===")

    # 不同提示词测试
    prompts_to_test = ["coolpapaers"]
    for prompt in prompts_to_test:
        logger.info(f"\n--- {prompt}提示词测试 ---")
        test_single_paper(TEST_PAPERS["single_paper"], prompt_name=prompt)
