# SmartPaper

SmartPaper 是一个智能论文阅读和分析工具,支持多种 LLM 接口(OpenAI、Deepseek、Kimi、豆包、智谱等),可以自动分析论文内容并生成结构化的分析报告。

## 功能特点

- 支持多种 LLM 提供商:
  - OpenAI
  - Deepseek
  - SiliconFlow
  - Kimi (Moonshot)
  - 豆包 (Doubao)
  - 智谱AI
- 支持多种输入方式:
  - 单个 PDF 文件
  - PDF 文件夹批量处理
  - 论文 URL
- 灵活的分析模式:
  - 单提示词模式: 使用预设的提示词模板进行分析
  - Agent 模式: 智能对话式分析 (开发中)
- 多种输出格式:
  - Markdown
  - CSV (开发中)
  - 结构化文件夹 (开发中)
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
  openai_deepseek:
    api_key: "your-api-key"
    base_url: "https://api.deepseek.com/v1"
    model: "deepseek-chat"
    temperature: 0.7
    max_tokens: 8192
```

### 3. 使用方法

#### 命令行使用

1. 查看帮助:
```bash
python main.py -h
```

2. 使用默认提示词模板分析论文:
```bash
python main.py https://arxiv.org/pdf/2312.12456.pdf
```

3. 指定提示词模板:
```bash
python main.py https://arxiv.org/pdf/2312.12456.pdf -p coolpapaers
```

4. 不提供URL时会使用默认论文URL:
```bash
python main.py -p yuanbao
```

#### 提示词模板

当前支持的提示词模板:
- `yuanbao`: 类似混元元宝的总结风格，包含研究背景、方法、实验设计和结果分析
- `coolpapaers`: 类似 papers.cool 的分析风格，包含问题定义、相关研究、解决方案、实验和未来方向
- `methodology`: 专注于研究方法论分析
- `results`: 专注于实验结果分析
- `contribution`: 专注于主要贡献分析
- `full_analysis`: 全面深入的分析

#### 输出结果

分析结果将保存在 `outputs` 目录下，文件名格式为 `analysis_prompt_{prompt_name}.md`。

示例输出:
```markdown
# 论文分析报告

## 元数据
- 标题: Example Paper
- 作者: John Doe
- URL: https://example.com/paper.pdf
- 分析时间: 2024-01-20T10:30:00

## 分析结果
[分析内容]
```

## 注意事项

1. API 密钥:
   - 请确保在配置文件中设置了正确的 API 密钥
   - 不同提供商的 API 密钥格式可能不同

2. URL 格式:
   - 目前主要支持 arXiv 的论文 URL
   - URL 必须直接指向 PDF 文件

3. 请求限制:
   - 默认限制为每次运行最多 10 次请求
   - 可以在配置文件中调整 `max_requests` 的值

4. 输出目录:
   - 程序会自动创建 `outputs` 目录
   - 同名文件会被覆盖，请注意备份

## 开发计划

- [ ] 支持 Agent 模式
- [ ] 添加 CSV 输出格式
- [ ] 添加结构化文件夹输出
- [ ] 支持更多论文来源
- [ ] 添加批量处理功能
- [ ] 添加进度显示
- [ ] 支持自定义提示词模板

## 贡献指南

欢迎提交 Issue 和 Pull Request!
