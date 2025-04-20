import os
import sys
import argparse
import traceback
from loguru import logger
from core.smart_paper_core import SmartPaper
from core.prompt_manager import list_prompts


def process_paper(
    url: str, prompt_name: str = "yuanbao", output_path: str = "outputs/analysis_prompt.md"
):
    """处理论文

    Args:
        url (str): 论文URL
        prompt_name (str): 提示词模板名称
        output_path (str): 输出文件路径
    """
    try:
        # 初始化SmartPaper
        reader = SmartPaper(output_format="markdown")
        logger.info(f"使用提示词模板: {prompt_name}")

        # 分析论文
        try:
            result = reader.process_paper_url(url, prompt_name=prompt_name)
        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            sys.exit(1)

        # 输出结果
        logger.info("分析结果:")
        print(result["result"])
        logger.info(f"分析结果已保存到: {output_path}")

        # 保存结果到文件
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["result"])

    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
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
    parser.add_argument("--output", "-o", default="outputs/analysis_prompt.md", help="输出文件路径")

    # 解析参数
    args = parser.parse_args()

    # 处理论文
    process_paper(args.url, args.prompt, args.output)


if __name__ == "__main__":
    # 显示可用的提示词模板
    logger.info("\n可用的提示词模板:")
    for name, desc in list_prompts().items():
        logger.info(f"- {name}: {desc}")
    logger.info()

    # 运行主函数
    main()
