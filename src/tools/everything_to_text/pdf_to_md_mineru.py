#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：筱可
# 2025-02-22
"""
#### 使用说明：
该模块用于将PDF文件转换为Markdown文件，并将生成的文件保存至指定的目录中。同时提供模型下载和配置功能。

#### 主要功能：
1. 将PDF文件转换为Markdown格式。
2. 提取PDF中的图片并保存。
3. 根据PDF解析模式（OCR或文本）进行处理。
4. 返回生成的Markdown文件路径。
5. 下载并配置必要的模型文件。

#### 参数说明：
1. mineru_pdf2md 函数：
    - pdf_path (str): 输入的PDF文件路径。
    - output_base_dir (str): 输出基础目录，默认为"outputs"。

    返回值：
        str: 生成的Markdown文件的绝对路径。

2. download_and_setup_models 函数：
    无需参数，自动下载并配置所需模型。

#### 注意事项：
1. 确保PDF文件路径正确，且输出目录存在。
2. 生成的输出目录将包括图片文件和Markdown文件，目录名会根据文件内容自动创建。
3. 首次使用时需要运行 download_and_setup_models 函数下载必要的模型。
4. 请确保网络连接正常，因为模型下载需要从远程服务器获取文件。

#### 更多信息：
无
"""

import os
import json
import requests
from modelscope import snapshot_download
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod
from loguru import logger


def download_json(url):
    """下载JSON配置文件"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def download_and_setup_models():
    """下载并设置必要的模型文件"""
    mineru_patterns = [
        "models/Layout/LayoutLMv3/*",
        "models/Layout/YOLO/*",
        "models/MFD/YOLO/*",
        "models/MFR/unimernet_small_2501/*",
        "models/TabRec/TableMaster/*",
        "models/TabRec/StructEqTable/*",
    ]
    model_dir = snapshot_download("opendatalab/PDF-Extract-Kit-1.0", allow_patterns=mineru_patterns)
    layoutreader_model_dir = snapshot_download("ppaanngggg/layoutreader")
    model_dir = model_dir + "/models"
    logger.info(f"model_dir is: {model_dir}")
    logger.info(f"layoutreader_model_dir is: {layoutreader_model_dir}")

    json_url = "https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/magic-pdf.template.json"
    config_file_name = "magic-pdf.json"
    home_dir = os.path.expanduser("~")
    config_file = os.path.join(home_dir, config_file_name)

    # 下载并修改配置文件
    json_data = download_json(json_url)
    json_data["models-dir"] = model_dir
    json_data["layoutreader-model-dir"] = layoutreader_model_dir

    with open(config_file, "w") as f:
        json.dump(json_data, f, indent=2)

    logger.info(
        f"The configuration file has been configured successfully, the path is: {config_file}"
    )


def mineru_pdf2md(pdf_path, output_base_dir="outputs"):
    """
    功能描述: 将PDF文件处理为Markdown格式。

    参数:
        pdf_path (str): PDF文件路径。
        output_base_dir (str): 输出基础目录，默认为"outputs"。

    返回值:
        str: 生成的Markdown文件路径。
    """
    os.makedirs(output_base_dir, exist_ok=True)  # 确保输出目录存在

    # 获取文件名和不带后缀的文件名
    pdf_file_name = os.path.basename(pdf_path)
    name_without_suff = pdf_file_name.split(".")[0]

    # 设置输出目录和图片存储目录
    local_image_dir = os.path.join(output_base_dir, "images")
    local_md_dir = output_base_dir
    image_dir = os.path.basename(local_image_dir)

    # 创建目录
    os.makedirs(local_image_dir, exist_ok=True)

    # 初始化数据读写器
    image_writer = FileBasedDataWriter(local_image_dir)
    md_writer = FileBasedDataWriter(local_md_dir)
    reader = FileBasedDataReader("")

    # 读取PDF文件内容
    pdf_bytes = reader.read(pdf_path)

    # 创建Dataset实例
    ds = PymuDocDataset(pdf_bytes)

    # 根据文档类型选择不同的处理方式（OCR模式或文本模式）
    if ds.classify() == SupportedPdfParseMethod.OCR:
        infer_result = ds.apply(doc_analyze, ocr=True)
        pipe_result = infer_result.pipe_ocr_mode(image_writer)
    else:
        infer_result = ds.apply(doc_analyze, ocr=False)
        pipe_result = infer_result.pipe_txt_mode(image_writer)

    # 获取并保存Markdown内容
    md_content = pipe_result.get_markdown(image_dir)
    output_md_path = os.path.join(local_md_dir, f"{name_without_suff}.md")

    # 将Markdown内容写入文件
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 返回生成的Markdown文件的绝对路径
    current_file_dir = os.path.abspath(os.path.dirname(__file__))
    abs_file_path = os.path.join(current_file_dir, output_md_path)
    return abs_file_path
