# PDF to Markdown 转换工具 (pdfplumber版)

## 简介

`pdf_to_md_pdfplumber` 是一个强大的PDF转换工具，基于pdfplumber库开发，能够提取PDF文档中的文本和图像，并将其转换为结构化的Markdown文档。本工具的特色是能够自动为提取的图像生成描述和标题，使输出的Markdown文档更加丰富和完整。

## 功能特性

- ✅ 完整的PDF文本内容提取
- 🖼️ 自动检测和提取PDF中的图像
- 🤖 使用AI技术自动生成图像描述和标题
- 📝 生成格式化的Markdown文档
- 🚀 支持异步处理，提高效率
- 💾 内置缓存系统，避免重复处理
- 📊 提供详细的处理进度和耗时统计

## 安装要求

要使用此工具，需要以下依赖：

```bash
pip install pdfplumber pillow uuid
```

如果需要使用AI图像描述功能，还需要安装相关依赖：

```bash
pip install asyncio
```

## 使用方法

### 命令行调用

```bash
python pdf_to_md_pdfplumber.py path/to/your/document.pdf [--output OUTPUT_DIR] [--api-key API_KEY]
```

参数说明:
- `pdf_path`: PDF文件路径（必填）
- `-o, --output`: 输出目录，可选，默认会创建一个自动命名的输出目录
- `-k, --api-key`: API密钥，用于图像处理API调用（可选）

### 作为模块导入

```python
from src.tools.everything_to_text.pdf_to_md_pdfplumber import process_pdf

# 基本使用
result = process_pdf("path/to/your/document.pdf")

# 指定输出目录
result = process_pdf("path/to/your/document.pdf", output_dir="./my_output")

# 指定API密钥
result = process_pdf("path/to/your/document.pdf", api_key="your-api-key")

# 使用转换器接口
from src.tools.everything_to_text.pdf_to_md_pdfplumber import pdfplumber_pdf2md

result = pdfplumber_pdf2md(
    file_path="path/to/your/document.pdf",
    config={
        "output_dir": "./output",
        "api_key": "your-api-key",
        "url": "custom-url-for-cache"  # 可选，用于缓存标识
    }
)
```

## 输出结构

工具处理PDF后将创建以下文件和目录：

```
output_directory/
├── document_name.md     # 转换后的Markdown文件
└── images/              # 提取的图片目录
    ├── page1_img1_uuid.png
    ├── page1_img2_uuid.png
    └── ...
```

处理结果的返回格式为：

```python
{
    "text_content": "# 文档标题\n\n## 第1页\n\n文本内容...",
    "metadata": {"title": "文档名称"},
    "images": [
        {"key": "page1_img1_uuid", "path": "完整路径", "filename": "文件名"}
    ]
}
```

## 图像处理功能

本工具的一个特色功能是能够自动为提取的图像生成描述和标题：

1. 提取图像：从PDF提取图像并保存
2. 生成描述：使用AI模型为图像生成详细描述
3. 生成标题：基于描述为图像创建简洁的标题
4. 集成到Markdown：自动将图像引用替换为带有标题和描述的格式

## 缓存系统

工具内置了缓存系统，可以避免重复处理相同的PDF：

- 首次处理时，结果会被缓存
- 再次处理时，如果PDF内容未变更，将直接从缓存加载结果
- 缓存使用文件路径或自定义URL作为标识符

## 高级功能

### 异步处理

本工具支持异步处理，大幅提高多图像文档的处理效率：

```python
import asyncio
from src.tools.everything_to_text.pdf_to_md_pdfplumber import process_pdf_async

async def main():
    result = await process_pdf_async("document.pdf")
    
asyncio.run(main())
```

### 自定义图像处理

可以通过修改配置来自定义图像处理行为：

```python
config = {
    "output_dir": "./output",
    "api_key": "your-api-key",
    "image_model": "Qwen/Qwen2.5-VL-72B-Instruct"  # 自定义图像模型
}

result = pdfplumber_pdf2md(file_path="document.pdf", config=config)
```

## 常见问题

**Q: 处理大型PDF文件时速度很慢怎么办？**  
A: 图像描述生成是最耗时的步骤。可以通过设置环境变量或直接传入API密钥来使用更快的API。

**Q: 如何提高图像描述的质量？**  
A: 本工具默认使用Qwen2.5-VL模型，这已经是一个高质量的图像描述模型。

**Q: 转换后的Markdown引用了错误的图像怎么办？**  
A: 工具使用了多种匹配策略来确保正确关联图像。如果仍有问题，可以查看日志输出找到匹配错误的原因。

## 性能指标

在典型配置下的性能参考：
- 文本提取：~0.5秒/页
- 图像提取：~0.2秒/图
- 图像描述生成：~3-5秒/图（取决于API响应速度）
- Markdown生成：~0.1秒/页

## 开发与贡献

欢迎贡献代码或提出建议！可以通过以下方式参与：

1. 提交Issue报告bug或提出功能请求
2. 提交Pull Request贡献代码
