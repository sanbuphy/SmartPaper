# PDF 转 Markdown 模块（无图像处理）

## 概述

`pdf_to_md_fitz.py` 是一个简单高效的 PDF 文本提取工具，它使用 PyMuPDF (fitz) 库将 PDF 文档转换为 Markdown 格式。该模块专注于文本内容的提取，不包含图像处理功能，适用于纯文本或对图像要求不高的场景。

## 依赖项

- Python 3.6+
- PyMuPDF (fitz)
- re (正则表达式库，Python 标准库)
- os (操作系统接口库，Python 标准库)

## 主要功能

### 1. 文本提取

从 PDF 文档中提取纯文本内容，页面布局将被转换为简单的文本流。

### 2. 参考文献过滤

可选择性地移除论文或报告中的参考文献部分，使转换后的内容更加专注于主体内容。

### 3. Markdown 输出

将提取的内容保存为 Markdown 格式，便于进一步编辑或处理。

## 核心函数

### `page_to_text(page_texts: Dict[int, str]) -> str`

将按页码存储的文本内容合并为完整的文档文本。

**参数:**
- `page_texts`: 按页码索引的文本字典，格式为 {页码: 文本内容}

**返回:**
- `str`: 合并后的完整文本

### `extract_pdf_content(pdf_path: str, output_dir: str, strip_references: bool = False) -> str`

提取 PDF 文档内容并可选择性地去除参考文献部分。

**参数:**
- `pdf_path`: PDF 文件路径
- `output_dir`: 输出目录
- `strip_references`: 是否去除参考文献部分，默认为 False

**返回:**
- `str`: 提取的文本内容

## 工作流程

1. 打开 PDF 文档
2. 逐页提取文本内容
3. 如果启用了 `strip_references` 选项，检测并移除参考文献部分
4. 将所有页面的文本合并为完整的文档
5. 返回提取的文本内容

## 使用示例

### 基本用法

```python
from SmartPaper.file_parsing.pdf_to_md_fitz import extract_pdf_content

# 提取 PDF 内容
text = extract_pdf_content(
    pdf_path="path/to/document.pdf",
    output_dir="path/to/output",
    strip_references=False
)

print(text)  # 打印提取的文本
```

### 去除参考文献

```python
from SmartPaper.file_parsing.pdf_to_md_fitz import extract_pdf_content

# 提取 PDF 内容并去除参考文献
text = extract_pdf_content(
    pdf_path="path/to/academic_paper.pdf",
    output_dir="path/to/output",
    strip_references=True  # 启用参考文献过滤
)

print(text)  # 打印提取的文本（不包含参考文献部分）
```

## 限制

1. **仅提取文本**：不处理图像、表格或其他非文本元素
2. **简单布局**：不保留复杂的文档布局，如多列文本
3. **参考文献识别限制**：仅通过关键词 "References" 或 "参考文献" 来识别参考文献部分
4. **语言限制**：参考文献识别仅支持英文和中文关键词

## 与其他模块的关系

此模块是 `pdf_to_md_fitz_with_image.py` 的简化版本，专注于文本提取。
对于需要保留图像的场景，建议使用 `pdf_to_md_fitz_with_image.py`。