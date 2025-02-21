# SmartPaper 测试目录结构

本目录包含 SmartPaper 项目的所有测试文件，按照功能模块进行分类组织。

## 目录结构

### core/ - 核心功能测试
- `test_paper_url.py`: 测试论文URL处理的核心功能，包括提示词模式和智能代理模式
- `test_stream.py`: 测试流式处理相关功能

### tools/ - 工具类测试
- `test_markdown_converter.py`: 测试各种格式文件到Markdown的转换功能
- `test_pdf_converter.py`: 测试PDF文件的处理和转换功能
- `test_arxiv_download_read.py`: 测试arXiv论文下载和读取功能

### integration/ - 集成测试
- `test_multiple_urls.py`: 测试多个URL的批量处理功能
- `test_single_local_papers.py`: 测试本地论文文件的完整处理流程
- `test_single_url.py`: 测试单个URL的完整处理流程

## 运行测试

你可以按照以下方式运行测试：

1. 运行所有测试：
```bash
python -m pytest tests/
```

2. 运行特定类别的测试：
```bash
python -m pytest tests/core/    # 运行核心功能测试
python -m pytest tests/tools/   # 运行工具类测试
python -m pytest tests/integration/  # 运行集成测试
```

3. 运行单个测试文件：
```bash
python -m pytest tests/core/test_paper_url.py
```
