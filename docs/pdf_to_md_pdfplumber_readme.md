# PDF转Markdown工具使用指南

## 简介

`pdf_to_md_pdfplumber.py` 是一个功能强大的PDF处理工具，可以将PDF文件转换为增强型Markdown格式，包含以下功能：

- 提取PDF文件中的所有文本内容
- 提取PDF文件中的所有图片
- 自动为图片生成AI描述和标题
- 将所有内容整合成一个结构化的Markdown文档

该工具利用了OpenAI的图像识别技术，能够智能分析图片内容并生成准确的描述和标题，大大提升了文档的可访问性和理解性。

## 特点

- **高质量文本提取**：使用pdfplumber库精确提取文本，保持页面结构
- **智能图像处理**：自动检测并提取PDF中的所有图像
- **AI图像描述**：对每张图片进行AI分析，生成详细描述
- **自动标题生成**：基于图片内容自动生成描述性标题
- **并发处理**：使用asyncio并发处理图片，提高效率
- **格式化输出**：生成格式规范、引用完整的Markdown文档
- **命令行支持**：提供简洁的命令行接口，易于集成到自动化流程中

## 安装依赖

请确保已安装以下依赖：

```bash
pip install pdfplumber pillow asyncio
```

图像描述功能依赖于我们的图像分析库，详见`src/tools/everything_to_text/image_to_text.py`。

## 使用方法

### 命令行使用

```bash
python pdf_to_md_pdfplumber.py <pdf文件路径> [-o <输出目录>] [-k <API密钥>]
```

参数说明：

- `<pdf文件路径>`: 必填，要处理的PDF文件路径
- `-o, --output`: 可选，指定输出目录，默认将创建时间戳子目录
- `-k, --api-key`: 可选，用于AI图像处理的API密钥，默认从环境变量读取

### 编程方式使用

```python
from src.tools.everything_to_text.pdf_to_md_pdfplumber import process_pdf

# 简单使用
process_pdf("path/to/your.pdf")

# 指定输出目录和API密钥
process_pdf("path/to/your.pdf", "./output_folder", "your-api-key")
```

## 输出文件说明

处理完成后，会在输出目录中生成以下文件：

1. `<pdf名称>.md`: 主要的Markdown文件，包含所有文本和图片引用
2. `images/`: 文件夹，包含提取的所有图片
3. `<pdf名称>_images.json`: 包含图片的base64编码数据的JSON文件

Markdown文件中的图片引用格式为：

```markdown
![图片标题](./images/图片文件名)

> 图片详细描述
```

## 高级配置

### 图像引擎配置

默认使用"Qwen/Qwen2.5-VL-72B-Instruct"模型来分析图像。如需调整，请修改`process_image_description_and_title`函数中的相关参数。

### 性能调优

对于大型PDF文件或包含大量图片的文件，可以考虑调整`process_image_async`函数中的并发设置以提高性能。

## 输出示例

处理完成的Markdown文件示例：

```markdown
# 示例文档

## 第1页

这是文档的正文内容...

![专业流程图](./images/page1_img1_12ab34cd.png)

> 这是一个展示项目工作流程的专业流程图，包含5个关键步骤：需求分析、设计、开发、测试和部署。每个步骤都用不同的颜色和图标表示，箭头显示了流程的先后顺序和关系。图表采用现代化设计风格，背景为浅蓝色。

---
```
