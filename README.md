# SmartPaper

SmartPaper 是一个智能论文阅读和分析工具,支持多种 LLM 接口(OpenAI、Deepseek、智谱等),可以自动分析论文内容并生成结构化的分析报告。

## 功能特点

- 支持多种 LLM 提供商:
  - OpenAI
  - Deepseek
  - SiliconFlow
  - 智谱AI
- 支持多种输入方式:
  - 单个 PDF 文件
  - PDF 文件夹批量处理
  - 论文 URL
- 灵活的分析模式:
  - 单提示词模式: 使用预设的提示词模板进行分析
  - Agent 模式: 智能对话式分析
- 多种输出格式:
  - Markdown
  - CSV
  - 结构化文件夹
- 可配置的提示词模板
- 请求次数限制保护

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

1. 复制并修改配置文件:
```bash
cp config/config.yaml.example config/config.yaml
```

2. 在 `config.yaml` 中设置你的 API 密钥和其他配置:
```yaml
llm:
  provider: "openai_deepseek"  # 选择 LLM 提供商
  max_requests: 10  # 最大请求次数限制
  openai_deepseek:
    api_key: "your-api-key"
    base_url: "https://api.deepseek.com/v1"
```

### 3. 快速测试

我们提供了几个测试脚本来验证功能:

1. 测试单个 URL:
```bash
python tests/test_single_url.py
```

2. 测试本地 PDF:
```bash
python tests/test_pdf_converter.py
```

3. 测试批量处理:
```bash
python tests/test_batch_papers.py
```

### 4. 使用示例

```python
from src.core.reader import SmartPaper

# 初始化
reader = SmartPaper(output_format='markdown')

# 处理单个论文 URL (提示词模式)
result = reader.process_paper_url(
    url="https://arxiv.org/pdf/2312.12456.pdf",
    mode="prompt",
    prompt_name="summary"
)

# 处理本地 PDF (Agent 模式)
result = reader.process_paper(
    file_path="papers/example.pdf",
    mode="agent"
)

# 批量处理文件夹
results = reader.process_directory(
    dir_path="papers/",
    mode="prompt",
    prompt_name="full_analysis"
)
```

## 提示词模板

当前支持的提示词模板:
- `summary`: 论文总体摘要分析
- `methodology`: 研究方法论分析
- `results`: 实验结果分析
- `contribution`: 主要贡献分析
- `full_analysis`: 全面深入分析

你可以在 `config/prompts.yaml` 中自定义新的提示词模板。

## 输出示例

1. Markdown 格式:
```markdown
# 论文分析报告

## 元数据
- 标题: Example Paper
- 作者: John Doe
- URL: https://example.com/paper.pdf
- 分析时间: 2024-01-20T10:30:00

## 分析结果
### Summary
...
```

2. CSV 格式包含以下字段:
- title
- url
- author
- date
- summary
- methodology
- results
- timestamp

3. 文件夹格式:
```
outputs/
  └── paper_analysis/
      ├── metadata.json
      ├── summary.md
      ├── methodology.md
      └── results.md
```

## 注意事项

1. 请求次数限制:
   - 默认限制为 10 次请求
   - 可以通过 `reset_request_count()` 重置计数器
   - 超过限制会抛出异常

2. 文件支持:
   - 支持常见的 PDF 文件格式
   - URL 必须直接指向 PDF 文件

3. 输出目录:
   - 默认输出到 `outputs/` 目录
   - 可以在配置文件中修改输出路径

## 开发计划

- [ ] 添加更多 LLM 提供商支持
- [ ] 改进 Agent 模式的对话能力
- [ ] 添加更多文件格式支持
- [ ] 添加 Web 界面
- [ ] 支持并行处理

## 贡献指南

欢迎提交 Issue 和 Pull Request!
