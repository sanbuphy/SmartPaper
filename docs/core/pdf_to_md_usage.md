# PDF转Markdown转换器使用文档

## 概述

`SmartPaper.core.pdf_to_md` 模块提供了一个灵活且可扩展的PDF到Markdown转换框架。该框架支持多种转换策略，目前实现了两种转换方式：基础的文本提取（fitz）和包含图像处理的增强版（fitz_with_image）。

## 快速开始

### 基本用法

下面是使用默认转换器（fitz）的基本示例：

```python
from SmartPaper.core.pdf_to_md import convert_pdf_to_markdown

# 使用基础转换器（仅文本）
markdown_text = convert_pdf_to_markdown(
    pdf_path="your_document.pdf",
    output_dir="output_folder"
)
print(f"提取的Markdown文本长度: {len(markdown_text)} 字符")
```

### 使用带图像的转换器

如果需要处理PDF中的图像，可以切换到带图像的转换器：

```python
from SmartPaper.core.pdf_to_md import convert_pdf_to_markdown

# 使用带图像的转换器
markdown_with_images = convert_pdf_to_markdown(
    pdf_path="your_document.pdf",
    output_dir="output_folder_with_images",
    converter_type="fitz_with_image",  # 切换到带图像的转换器
    strip_references=True,  # 可选：去除参考文献部分
    cache_base64=True,  # 可选：缓存图像的base64编码
    cache_dir="cache_folder"  # 可选：指定缓存目录
)
```

## 转换器类型

目前支持的转换器类型有：

1. `fitz` (默认) - 基于PyMuPDF的基础转换器，仅提取文本内容
2. `fitz_with_image` - 基于PyMuPDF的增强转换器，提取文本内容并处理图像

## 详细API

### 便捷函数

```python
convert_pdf_to_markdown(
    pdf_path: str,
    output_dir: str,
    converter_type: str = 'fitz',
    strip_references: bool = False,
    api_key: Optional[str] = None,
    delete_rendered_images: bool = True,
    cache_base64: bool = True,
    cache_dir: Optional[str] = None
) -> str
```

**参数说明：**

- `pdf_path` - PDF文件路径
- `output_dir` - 输出目录，用于存储生成的Markdown文件和相关资源
- `converter_type` - 转换器类型，可选值：'fitz'（默认）或'fitz_with_image'
- `strip_references` - 是否去除参考文献部分，默认为False
- `api_key` - 图像分析API密钥，仅在使用fitz_with_image转换器时有效
- `delete_rendered_images` - 是否删除渲染后的页面图像，默认为True
- `cache_base64` - 是否缓存图像的base64编码，默认为True
- `cache_dir` - 缓存目录路径，若为None则使用默认目录

**返回值：**

- `str` - 转换后的Markdown文本内容

### 工厂类

如果需要更高级的控制，可以直接使用`PDFConverter`工厂类：

```python
from SmartPaper.core.pdf_to_md import PDFConverter

# 创建转换器实例
converter = PDFConverter(converter_type="fitz_with_image")

# 执行转换
markdown_text = converter.convert_pdf_to_markdown(
    pdf_path="your_document.pdf",
    output_dir="output_folder",
    strip_references=True
)
```

## 扩展转换器

您可以创建自己的PDF转换器实现，只需遵循以下步骤：

1. 创建一个继承自`PDFToMarkdownConverter`的新类
2. 实现`convert`方法
3. 注册您的转换器

示例：

```python
from SmartPaper.core.pdf_to_md import PDFToMarkdownConverter, PDFConverter

class MyCustomPDFConverter(PDFToMarkdownConverter):
    def convert(self, pdf_path: str, output_dir: str, **kwargs) -> str:
        # 自定义转换逻辑
        # ...
        return converted_text

# 注册自定义转换器
PDFConverter.register_converter("my_custom", MyCustomPDFConverter)

# 使用自定义转换器
markdown_text = convert_pdf_to_markdown(
    pdf_path="your_document.pdf",
    output_dir="output_folder",
    converter_type="my_custom"
)
```

## 高级用例

### 1. 处理大型学术论文

对于包含大量参考文献的学术论文，可以使用`strip_references`参数去除参考文献部分：

```python
markdown_text = convert_pdf_to_markdown(
    pdf_path="academic_paper.pdf",
    output_dir="output_folder",
    strip_references=True
)
```

### 2. 批量处理多个PDF文件

```python
import os
from SmartPaper.core.pdf_to_md import convert_pdf_to_markdown

def batch_convert_pdfs(pdf_folder, output_base_folder, converter_type="fitz"):
    """批量转换文件夹中的所有PDF文件"""
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            # 为每个PDF创建单独的输出文件夹
            base_name = os.path.splitext(filename)[0]
            output_dir = os.path.join(output_base_folder, base_name)
            
            print(f"转换: {filename}")
            convert_pdf_to_markdown(
                pdf_path=pdf_path,
                output_dir=output_dir,
                converter_type=converter_type
            )
            print(f"完成: {filename} -> {output_dir}\n")

# 使用示例
batch_convert_pdfs("papers_folder", "converted_papers")
```

### 3. 集成图像处理

当使用`fitz_with_image`转换器时，您可以提供额外的图像处理配置：

```python
markdown_text = convert_pdf_to_markdown(
    pdf_path="image_rich_document.pdf",
    output_dir="output_with_images",
    converter_type="fitz_with_image",
    api_key="your_vision_api_key",  # 用于图像分析的API密钥
    cache_base64=True,              # 缓存图像base64编码以提高性能
    cache_dir="image_cache"         # 自定义缓存目录
)
```

## 故障排除

### 常见问题

1. **内存错误**：处理大型PDF或包含大量图像的PDF时可能遇到内存不足问题。解决方案：
   - 使用`fitz`转换器代替`fitz_with_image`
   - 考虑增加系统内存或减小处理的PDF大小

2. **图像提取质量问题**：如果提取的图像质量不理想，可尝试：
   - 确保使用最新版本的PyMuPDF库
   - 在使用`fitz_with_image`转换器时提供有效的API密钥以获取更好的图像分析结果

3. **中文字符显示问题**：对于包含中文字符的PDF，确保系统安装了适当的字体，并且输出文件使用UTF-8编码。

## 注意事项

- 对于包含复杂布局或特殊格式的PDF，转换后的Markdown可能需要手动调整。
- 图像提取功能需要足够的系统资源，特别是处理高分辨率图像时。
- 请确保有适当的权限访问和修改指定的输出目录。

## 完整示例

```python
from SmartPaper.core.pdf_to_md import convert_pdf_to_markdown
import os

# 确保输出目录存在
output_dir = "output_folder"
os.makedirs(output_dir, exist_ok=True)

# 转换PDF
markdown_text = convert_pdf_to_markdown(
    pdf_path="example.pdf",
    output_dir=output_dir,
    converter_type="fitz_with_image",
    strip_references=True,
    delete_rendered_images=False  # 保留渲染后的页面图像，用于调试
)

# 输出结果
print(f"成功转换PDF。Markdown文本长度: {len(markdown_text)} 字符")
print(f"Markdown文件保存在: {os.path.join(output_dir, 'output.md')}")
```