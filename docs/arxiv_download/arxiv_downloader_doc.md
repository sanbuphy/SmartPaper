# ArxivDownloader 模块文档

## 简介

`arxiv_downloader.py` 模块提供了下载 arXiv 论文 PDF 文件的功能。该模块与 `arxiv_client.py` 无缝集成，可以同时获取论文的元数据和 PDF 文件。

## 依赖项

本模块依赖以下 Python 库：
- os
- logging
- requests
- pathlib.Path
- typing
- SmartPaper.get_arxiv.arxiv_client (内部依赖)

## 函数

### download_paper

```python
def download_paper(
    paper_id: str,
    output_dir: Union[str, Path],
    filename: Optional[str] = None,
    get_metadata: bool = True,
) -> Tuple[str, Optional[ArxivPaper]]
```

下载 arXiv 论文的 PDF 文件的主要函数。

#### 参数

| 参数名 | 类型 | 描述 | 是否必需 | 默认值 |
|-------|-----|------|---------|--------|
| paper_id | str | arXiv 论文 ID，如 "1706.03762" 或完整的链接 | 是 | - |
| output_dir | Union[str, Path] | 保存 PDF 的目录 | 是 | - |
| filename | Optional[str] | 文件名（不含扩展名），如果为 None，则使用论文 ID 或元数据生成 | 否 | None |
| get_metadata | bool | 是否获取论文的元数据 | 否 | True |

#### 返回值

函数返回一个元组，包含两个元素：
1. **PDF 文件路径**：字符串类型，表示保存的 PDF 文件的完整路径
2. **论文元数据**：ArxivPaper 对象或 None（如果 get_metadata=False 或获取元数据失败）

#### 功能流程

1. **ID 处理**：
   - 从完整链接中提取 arXiv ID
   - 去除版本号（如 "v1"、"v2" 等）

2. **目录准备**：
   - 确保输出目录存在，如果不存在则创建

3. **元数据获取**（可选）：
   - 如果 get_metadata=True，尝试获取论文元数据
   - 如果成功且未指定文件名，使用元数据生成文件名

4. **文件名处理**：
   - 如果未指定文件名且无法获取元数据，使用论文 ID 作为文件名
   - 确保文件名以 .pdf 结尾

5. **PDF 下载**：
   - 构建 PDF URL
   - 以流式方式下载 PDF 文件
   - 检查下载内容是否为有效的 PDF
   - 将内容写入目标文件

6. **返回结果**：
   - 返回保存的 PDF 路径和论文元数据（如果有）

#### 异常处理

函数处理以下异常情况：
- 无法获取论文元数据
- 网络请求失败
- 下载的内容不是有效的 PDF
- 写入文件失败

所有异常会被记录到日志中，并向上层调用者抛出异常。

## 使用示例

### 基本用法

```python
from SmartPaper.get_arxiv import download_paper

# 下载论文（含元数据）
pdf_path, metadata = download_paper(
    paper_id="1706.03762",  # Transformer 论文
    output_dir="./papers"
)

print(f"论文已下载至: {pdf_path}")
if metadata:
    print(f"论文标题: {metadata.title}")
    print(f"作者: {', '.join(metadata.authors)}")
```

### 仅下载 PDF（不获取元数据）

```python
from SmartPaper.get_arxiv import download_paper

# 仅下载 PDF
pdf_path, _ = download_paper(
    paper_id="1706.03762",
    output_dir="./papers",
    get_metadata=False
)

print(f"论文已下载至: {pdf_path}")
```

### 使用自定义文件名

```python
from SmartPaper.get_arxiv import download_paper

# 使用自定义文件名
pdf_path, metadata = download_paper(
    paper_id="1706.03762",
    output_dir="./papers",
    filename="transformer_paper"  # 将自动添加 .pdf 扩展名
)

print(f"论文已下载至: {pdf_path}")
```

### 从 URL 下载

```python
from SmartPaper.get_arxiv import download_paper

# 从 arXiv URL 下载
pdf_path, metadata = download_paper(
    paper_id="https://arxiv.org/abs/1706.03762v5",  # 完整 URL，会自动提取 ID 并去除版本
    output_dir="./papers"
)

print(f"论文已下载至: {pdf_path}")
```

## 与 ArxivClient 结合使用

该模块可以与 `ArxivClient` 结合使用，实现更复杂的功能：

```python
from SmartPaper.get_arxiv import ArxivClient, download_paper

# 搜索相关论文
client = ArxivClient()
papers = client.search("transformer attention mechanism", max_results=3)

# 下载搜索到的所有论文
for paper in papers:
    pdf_path, _ = download_paper(
        paper_id=paper.paper_id,
        output_dir="./papers",
        filename=paper.filename,  # 使用 ArxivPaper 的 filename 方法
        get_metadata=False  # 已经有元数据，不需要再次获取
    )
    print(f"已下载: {paper.title} -> {pdf_path}")
```

## 注意事项

1. 函数会自动处理 arXiv ID 的不同格式，包括旧格式（如 "math.AG/0309225"）和新格式（如 "1706.03762"）。
2. 下载大量论文时，请留意 arXiv 的访问限制，避免过于频繁的请求。
3. 如果同时需要获取多篇论文的元数据和 PDF，建议先使用 `ArxivClient` 批量获取元数据，然后使用 `download_paper` 下载 PDF，避免重复请求。