"""
#### 使用说明：

此代码用于将指定的 PDF 文件转换为 Markdown 格式，并可选择是否执行 OCR 解析。它支持自定义输出路径及图片子目录，并根据 PDF 文件的解析方式生成结果。运行前需要确保已下载相关模型文件。

#### 主要功能：
- 解析 PDF 文件，支持 OCR 解析模式与文本解析模式。
- 支持将解析后的结果输出为 Markdown 文件。
- 支持生成图片，并将其存储在指定子目录下。
- 根据解析的结果生成多种输出，包括基础内容和详细的布局、模型、跨度图。

#### 参数说明：

- **process_pdf函数**：
  - `pdf_file_name (str)`: PDF 文件的绝对路径。
  - `output_dir (str)`: 存放输出文件的绝对路径目录。
  - `image_subdir (str)`: 存放图片的子目录名称（默认为 "images"）。
  - `simple_output (bool)`: 是否只输出基础结果（默认为 True）。
  - **返回值**：返回生成的 Markdown 文件的绝对路径。

#### 注意事项：
- 运行此代码前，请确保运行 `download_models.py` 下载模型文件，否则会报错 "没有找到 magic pdf.json 文件"。
- `output_dir` 和 `pdf_file_name` 必须为绝对路径，否则会抛出异常。
- 生成的 Markdown 文件会存储在与 PDF 文件同名的目录下，并包含所有解析结果。

#### 更多信息：
- 本代码依赖 `magic_pdf` 库，该库需要模型文件才能正常运行。请确保先运行 `download_models.py` 下载所需的模型。
- 本代码可以生成 OCR 和文本解析两种模式的结果，具体模式取决于 PDF 文件的内容。


"""

import os
import uuid
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod


def process_pdf(pdf_file_name, output_dir, image_subdir="images", simple_output=True):
    """
    使用指定的 PDF 文件名进行解析、OCR及结果输出。

    参数:
        pdf_file_name (str): PDF 文件的绝对路径
        output_dir (str): 存放输出文件的绝对路径目录
        image_subdir (str): 存放图片的子目录名称
        simple_output (bool): 是否只输出基础结果
    返回:
        abs_md_file_path (str): 生成的 Markdown 文件的绝对路径
    """
    # 确保输入的 output_dir 是绝对路径
    if not os.path.isabs(output_dir):
        raise ValueError("output_dir 必须是绝对路径")

    # 确保输入的 pdf_file_name 是绝对路径
    if not os.path.isabs(pdf_file_name):
        raise ValueError("pdf_file_name 必须是绝对路径")

    # 从 PDF 文件名称中去掉后缀，用于生成输出目录及文件名
    name_without_suff = os.path.splitext(os.path.basename(pdf_file_name))[0]
    # 生成唯一 ID，确保输出目录不冲突
    unique_id = uuid.uuid4()
    # 组合输出目录和图片目录
    output_subdir = f"{name_without_suff}-{unique_id}"
    local_image_dir = os.path.join(output_dir, output_subdir, image_subdir)
    local_md_dir = os.path.join(output_dir, output_subdir)

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
    md_file_path = os.path.join(local_md_dir, f"{name_without_suff}.md")
    abs_md_file_path = os.path.abspath(md_file_path)

    # 根据 simple_output 控制输出的详细程度
    if simple_output:
        pipe_result.dump_md(md_writer, f"{name_without_suff}.md", os.path.basename(local_image_dir))
        pipe_result.dump_content_list(
            md_writer, f"{name_without_suff}_content_list.json", os.path.basename(local_image_dir)
        )
    else:
        pipe_result.dump_md(md_writer, f"{name_without_suff}.md", os.path.basename(local_image_dir))
        pipe_result.dump_content_list(
            md_writer, f"{name_without_suff}_content_list.json", os.path.basename(local_image_dir)
        )
        infer_result.draw_model(os.path.join(local_md_dir, f"{name_without_suff}_model.pdf"))
        pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"))
        pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_suff}_spans.pdf"))

    # 返回生成的 Markdown 文件绝对路径
    return abs_md_file_path
