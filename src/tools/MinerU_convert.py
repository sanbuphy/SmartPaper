# author: 筱可
# date：2025年02月19日

"""
注意：运行此文件之前必须运行download_models.py下载模型文件
否则：报错没有找到magic pdf.json文件
"""

import os
import uuid
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

def process_pdf(
                pdf_file_name,
                output_dir="outputs",
                image_subdir="images",
                simple_output=True):
    """
    使用指定的 PDF 文件名进行解析、OCR及结果输出。
    
    参数:
        pdf_file_name (str): PDF 文件名称
        output_dir (str): 存放输出文件的目录
        image_subdir (str): 存放图片的子目录名称
        simple_output (bool): 是否只输出基础结果 
    返回:
        abs_md_file_path (str): 生成的 Markdown 文件的绝对路径
    """
    # 获取当前脚本所在目录，拼接输出目录路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_output_dir = os.path.join(script_dir, output_dir)

    # 从 PDF 文件名称中去掉后缀，用于生成输出目录及文件名
    name_without_suff = pdf_file_name.split(".")[-2]
    # 生成唯一 ID，确保输出目录不冲突
    unique_id = uuid.uuid4()
    # 组合输出目录和图片目录
    output_subdir = f"{name_without_suff}-{unique_id}"
    local_image_dir = os.path.join(absolute_output_dir, output_subdir, image_subdir)
    local_md_dir = os.path.join(absolute_output_dir, output_subdir)

    # 创建输出结果所需的目录
    os.makedirs(local_image_dir, exist_ok=True)
    os.makedirs(local_md_dir, exist_ok=True)

    # 初始化写入器与读取器，用于处理 PDF 与生成文件
    image_writer = FileBasedDataWriter(local_image_dir)
    md_writer = FileBasedDataWriter(local_md_dir)
    reader1 = FileBasedDataReader("")
    
    # 读取 PDF 文件的字节内容
    pdf_bytes = reader1.read(pdf_file_name)

    # 生成与分析 PDF 的数据集
    ds = PymuDocDataset(pdf_bytes)
    pdf_parse_method = ds.classify()  # 获取 PDF 解析方式

    # 根据 PDF 解析方式选择是否启用 OCR
    if pdf_parse_method == SupportedPdfParseMethod.OCR:
        infer_result = ds.apply(doc_analyze, ocr=True)
        pipe_result = infer_result.pipe_ocr_mode(image_writer)
    else:
        infer_result = ds.apply(doc_analyze, ocr=False)
        pipe_result = infer_result.pipe_txt_mode(image_writer)

    # 计算 Markdown 文件的路径
    md_file_path = os.path.join(os.getcwd(), local_md_dir, f"{name_without_suff}.md")
    abs_md_file_path = os.path.abspath(md_file_path)

    # 根据 simple_output 控制输出的详细程度
    if simple_output:
        pipe_result.dump_md(md_writer, f"{name_without_suff}.md", os.path.basename(local_image_dir))
        pipe_result.dump_content_list(md_writer,
                                      f"{name_without_suff}_content_list.json",
                                      os.path.basename(local_image_dir))
    else:
        pipe_result.dump_md(md_writer, f"{name_without_suff}.md", os.path.basename(local_image_dir))
        pipe_result.dump_content_list(md_writer,
                                      f"{name_without_suff}_content_list.json",
                                      os.path.basename(local_image_dir))
        infer_result.draw_model(os.path.join(local_md_dir, f"{name_without_suff}_model.pdf"))
        pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"))
        pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_suff}_spans.pdf"))

    # 返回生成的 Markdown 文件绝对路径
    return abs_md_file_path
