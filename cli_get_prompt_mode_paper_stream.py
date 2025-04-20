import os
import sys
import argparse
import yaml
import traceback
from loguru import logger
from core.smart_paper_core import SmartPaper
from core.prompt_manager import list_prompts


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def process_paper(url: str, prompt_name: str = "yuanbao"):
    """处理论文

    Args:
        url (str): 论文URL
        prompt_name (str): 提示词模板名称
    """
    try:
        logger.info(f"使用提示词模板: {prompt_name}")

        # 创建输出目录及输出文件
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"analysis_prompt_{prompt_name}.md")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("")

        # 初始化SmartPaper
        reader = SmartPaper(output_format="markdown")

        # 流式处理论文并实时输出
        logger.info("分析结果:\n")

        # 使用流式处理
        for chunk in reader.process_paper_url_stream(url, prompt_name=prompt_name):
            # 流式打印到控制台
            print(chunk, end="", flush=True)
            # 追加写入输出文件
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(chunk)
        print("\n")

        logger.info(f"分析结果已保存到: {output_file}")

    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        # 打印完整的错误栈信息
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    # 显示可用的提示词模板
    logger.info("\n可用的提示词模板:")
    for name, desc in list_prompts().items():
        logger.info(f"- {name}: {desc}")

    parser = argparse.ArgumentParser(description="论文分析工具")
    parser.add_argument(
        "url", nargs="?", default="https://arxiv.org/pdf/2305.12002", help="论文URL"
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default="coolpapaers",
        choices=list_prompts().keys(),
        help="提示词模板名称",
    )

    args = parser.parse_args()
    process_paper(args.url, args.prompt)


if __name__ == "__main__":
    main()
