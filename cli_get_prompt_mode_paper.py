import os
import sys
import argparse
from loguru import logger
from src.core.reader import SmartPaper
from src.core.prompt_library import list_prompts


def process_paper(url: str, prompt_name: str = "yuanbao"):
    """处理论文

    Args:
        url (str): 论文URL
        prompt_name (str): 提示词模板名称
    """
    try:
        # 初始化SmartPaper
        reader = SmartPaper(output_format="markdown")
        logger.info(f"使用提示词模板: {prompt_name}")

        # 处理论文
        result = reader.process_paper_url(url, mode="prompt", prompt_name=prompt_name)

        # 创建输出目录
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)

        # 保存结果
        output_file = os.path.join(output_dir, f"analysis_prompt_{prompt_name}.md")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["result"])

        logger.info(f"分析结果已保存到: {output_file}")

    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        sys.exit(1)


def main():
    """主函数"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="论文分析工具")
    parser.add_argument(
        "url", nargs="?", default="https://arxiv.org/pdf/2305.12002", help="论文URL"
    )
    parser.add_argument(
        "--prompt", "-p", default="yuanbao", choices=list_prompts().keys(), help="提示词模板名称"
    )

    # 解析参数
    args = parser.parse_args()

    # 处理论文
    process_paper(args.url, args.prompt)


if __name__ == "__main__":
    # 显示可用的提示词模板
    print("\n可用的提示词模板:")
    for name, desc in list_prompts().items():
        print(f"- {name}: {desc}")
    print()

    # 运行主函数
    main()
