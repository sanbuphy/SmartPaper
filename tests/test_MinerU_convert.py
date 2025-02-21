import sys
import os
from  src.tools.mineru_convert import process_pdf
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 主程序入口
if __name__ == "__main__":
    pdf_file_name = "如何阅读一本书-output.pdf"  # 指定要处理的PDF文件名
    md_file_path = process_pdf(pdf_file_name)  # 处理PDF文件并获取生成的markdown文件路径
    print(f"生成的Markdown文件路径: {md_file_path}")
