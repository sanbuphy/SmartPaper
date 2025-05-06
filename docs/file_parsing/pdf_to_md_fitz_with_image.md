# PDF 转 Markdown 模块（带图像处理）

## 概述

`pdf_to_md_fitz_with_image.py` 是一个高级 PDF 文档解析工具，专门用于将 PDF 文档转换为 Markdown 格式，同时保留和处理文档中的图像内容。该模块使用 PyMuPDF (fitz) 进行 PDF 解析，并集成了高级图像处理和版面分析功能，适用于学术论文、技术报告等包含丰富图像、表格的复杂文档。

## 依赖项

- Python 3.6+
- PyMuPDF (fitz)
- re (正则表达式库，Python 标准库)
- os (操作系统接口库，Python 标准库)
- SmartPaper.file_parsing.image_utils 模块 (内部依赖)

## 主要功能

### 1. 文本提取

从 PDF 文档中逐页提取文本内容，保持文本顺序和结构。

### 2. 图像提取和处理

识别、提取 PDF 中的图像、表格和图表，并进行版面分析以确定它们的正确位置。

### 3. 参考文献过滤

可选择性地移除论文或报告中的参考文献部分。

### 4. 图像缓存

支持图像缓存功能，避免重复处理相同的图像内容，提高效率。

### 5. Markdown 生成

将提取的文本和图像内容整合生成完整的 Markdown 文档，图像以相对路径引用。

## 核心函数

### `page_to_text(page_texts: Dict[int, str]) -> str`

将按页码存储的文本内容合并为完整的文档文本。

**参数:**
- `page_texts`: 按页码索引的文本字典，格式为 {页码: 文本内容}

**返回:**
- `str`: 合并后的完整文本

### `advanced_image_handler(page: pm.Page, page_num: int, output_dir: str, api_key: Optional[str] = None, delete_rendered_image: bool = True, cache_base64: bool = True, cache_dir: Optional[str] = None) -> str`

高级图像处理函数，用于处理 PDF 页面中的图像，提取并分析图像内容。

**参数:**
- `page`: PDF 页面对象
- `page_num`: 页码（从1开始）
- `output_dir`: 输出目录
- `api_key`: 图像分析API密钥（可选）
- `delete_rendered_image`: 是否删除处理后的渲染页面图像，默认为 True
- `cache_base64`: 是否缓存图像的 base64 编码，默认为 True
- `cache_dir`: 缓存目录路径，若为 None 则使用默认目录

**返回:**
- `str`: 包含图像的 Markdown 文本

### `extract_pdf_content(pdf_path: str, output_dir: str, strip_references: bool = False, image_handler: Optional[Callable] = None, api_key: Optional[str] = None, delete_rendered_images: bool = True, cache_base64: bool = True, cache_dir: Optional[str] = None) -> str`

提取 PDF 文档内容，包括文本和图像，并生成 Markdown 文件。

**参数:**
- `pdf_path`: PDF 文件路径
- `output_dir`: 输出目录
- `strip_references`: 是否去除参考文献部分，默认为 False
- `image_handler`: 图像处理函数，用于提取和处理图像
- `api_key`: 图像分析API密钥（可选）
- `delete_rendered_images`: 是否删除渲染后的页面图像，默认为 True
- `cache_base64`: 是否缓存图像的 base64 编码，默认为 True
- `cache_dir`: 缓存目录路径，若为 None 则使用默认目录

**返回:**
- `str`: 生成的 Markdown 内容

### `default_image_handler(page: pm.Page, page_num: int, output_dir: str) -> None`

简单图像处理函数（示例），将页面转换为图像并保存到指定目录。此函数仅作为示例，实际使用 advanced_image_handler。

**参数:**
- `page`: PDF 页面对象
- `page_num`: 页码（从1开始）
- `output_dir`: 输出目录

## 工作流程

1. 打开 PDF 文档
2. 为输出创建必要的目录结构
3. 逐页处理 PDF 内容：
   - 提取文本内容
   - 使用图像处理器提取和分析图像（如果提供了图像处理函数）
   - 如果启用了参考文献过滤，检测并移除参考文献部分
4. 关闭 PDF 文档
5. 合并文本和图像内容，生成完整的 Markdown 文档
6. 保存 Markdown 文件和图像文件
7. 返回生成的 Markdown 内容

## 版面分析和图像处理

该模块在 `advanced_image_handler` 函数中使用了复杂的版面分析技术：

1. **页面渲染**：将 PDF 页面渲染为高质量图像（缩放因子 4.0）
2. **版面分析**：使用 `sort_page_layout` 函数分析页面布局
3. **图像标识**：识别多种类型的图像元素（图片、表格、图表等）
4. **图像提取**：从布局中提取图像并转换为 Markdown 格式
5. **资源清理**：处理完成后可选择性地删除临时渲染图像

## 使用示例

### 基本用法（带图像处理）

```python
from SmartPaper.file_parsing.pdf_to_md_fitz_with_image import extract_pdf_content, advanced_image_handler

# 提取 PDF 内容，包括图像处理
markdown_text = extract_pdf_content(
    pdf_path="path/to/document.pdf",
    output_dir="path/to/output",
    strip_references=False,
    image_handler=advanced_image_handler,  # 使用高级图像处理
    delete_rendered_images=True,
    cache_base64=True
)

print(f"生成的 Markdown 长度: {len(markdown_text)} 字符")
```

### 使用自定义 API 密钥（用于图像分析）

```python
from SmartPaper.file_parsing.pdf_to_md_fitz_with_image import extract_pdf_content, advanced_image_handler

# 使用 API 密钥进行图像分析
markdown_text = extract_pdf_content(
    pdf_path="path/to/document.pdf",
    output_dir="path/to/output",
    image_handler=advanced_image_handler,
    api_key="your_api_key_here",  # 提供 API 密钥
    cache_dir="path/to/custom/cache"  # 自定义缓存目录
)
```

### 仅文本提取（不处理图像）

```python
from SmartPaper.file_parsing.pdf_to_md_fitz_with_image import extract_pdf_content

# 不指定 image_handler，只提取文本
text_only = extract_pdf_content(
    pdf_path="path/to/document.pdf",
    output_dir="path/to/output",
    strip_references=True  # 去除参考文献
)
```

## 高级配置

### 缓存配置

模块支持两级缓存机制：
1. **图像缓存**：后续可以使用cache内的图片base64编码替换前端部分的图片进行展示。
2. **缓存目录**：通过 `cache_dir` 参数指定自定义缓存位置。

### 图像处理配置

1. **渲染质量**：通过 `page2image` 函数中的 `zoom_factor` 参数调整（默认为 4.0）
2. **可识别图像类型**：通过 `image_labels` 集合配置，支持多语言标签
3. **资源管理**：通过 `delete_rendered_image` 参数控制是否保留临时图像

## 限制与注意事项

1. **处理速度**：由于包含图像处理和版面分析，速度会慢于纯文本提取
2. **内存占用**：处理大型或图像密集的 PDF 可能需要较多内存
3. **API 依赖**：某些高级图像分析功能可能需要外部 API 密钥
4. **参考文献识别**：仅支持通过关键词 "References" 或 "参考文献" 识别

## 与其他模块的关系

此模块是 `pdf_to_md_fitz.py` 的增强版本，添加了完整的图像处理和版面分析功能。
如果只需要提取文本内容，建议使用更轻量级的 `pdf_to_md_fitz.py` 模块。