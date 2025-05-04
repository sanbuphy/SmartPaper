# 把SmartPaper的路径添加到sys.path中
import sys
import os
# 上一级目录是tests，再上一级目录是SmartPaper
# 这段代码的作用是将当前文件所在目录的上两级目录添加到Python的模块搜索路径中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SmartPaper.file_parsing.pdf_to_md_fitz import extract_pdf_content


def main() -> None:
    pdf_file: str = "../test_datas/test.pdf" 
    output_dir: str = "../test_datas/outputs/test_pdf_to_md_fitz_output"  

    strip_references: bool = True  

    full_text: str = extract_pdf_content(
        pdf_file,
        output_dir,
        strip_references=strip_references,
    )
    print(full_text)


if __name__ == "__main__":
    main()
