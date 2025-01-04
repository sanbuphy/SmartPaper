"""
将 PDF 文件转换为 Markdown 格式的文本
"""
import os
import fitz as pm
import re
from typing import Dict, List, Optional, Union


def page_to_text(page_texts: Dict[int, str]) -> str:
    markdown_content: List[str] = []
    for page_num in sorted(page_texts.keys()):
        markdown_content.append(page_texts[page_num])
    full_text: str = "\n\n".join(markdown_content)
    
    return full_text

def extract_pdf_content(pdf_path: str, output_dir: str, strip_references: bool = False) -> str:

    pdf_document: pm.Document = pm.open(pdf_path)

    page_texts: Dict[int, str] = {}

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)


    total_pages: int = len(pdf_document)

    references_found: bool = False
    for page_num in range(total_pages):

        page: pm.Page = pdf_document[page_num]
        current_page_text: str = page.get_text()

        if strip_references:
            match: Optional[re.Match] = re.search(r"^\s*(References|参考文献)\s*$", current_page_text, re.IGNORECASE | re.MULTILINE)

            if match:
            
                reference_start_index: int = match.start()

                current_page_text = current_page_text[:reference_start_index].rstrip()
                references_found = True

                page_texts[page_num + 1] = current_page_text
                print(f"Found references on page {page_num + 1}.")
                # 调试使用
                # exit()
                break 

        # 如果没有找到参考文献，或者未启用 strip_references，正常存储页面内容
        if not references_found:
            
            page_texts[page_num + 1] = current_page_text

    pdf_document.close()

    full_text: str = page_to_text(page_texts)

    return full_text


def main() -> None:
    pdf_file: str = "test.pdf" 
    output_dir: str = "outputs/test_pdf_to_md_fitz"  

    strip_references: bool = True  

    full_text: str = extract_pdf_content(
        pdf_file,
        output_dir,
        strip_references=strip_references,
    )
    print(full_text)


if __name__ == "__main__":
    main()
