# 配置文件 (config.yaml) 使用说明

## 概述

配置文件是 SmartPaper 系统的核心组件，用于定义系统的行为和参数。本文档将详细介绍配置文件的结构、各部分的作用以及使用注意事项。

## 配置文件结构

配置文件采用 YAML 格式，主要包含以下几个部分：

1. LLM 配置
2. VLM 配置
3. 文档转换器配置
4. 输出配置
5. 提示词配置
6. Agent 配置

## LLM 配置详解

LLM (大型语言模型) 配置是整个系统的核心，定义了系统如何与各种 AI 模型进行交互。

```yaml
llm:
  provider: "openai_deepseek"  # 提供商选择
  max_requests: 10  # 最大请求次数限制
  default_model_index: 0  # 默认使用模型的索引
  # 各提供商的具体配置
  openai:
    # 配置详情...
  openai_deepseek:
    # 配置详情...
  # 其他提供商...
```

### 重要参数说明

#### `provider`

指定当前使用的 LLM 提供商。可选项包括：
- openai
- openai_deepseek
- openai_siliconflow
- openai_kimi
- openai_doubao
- zhipuai
- ai_studio
- ai_studio_fast_deploy

#### `default_model_index` 和 `models` 的关系

这是配置中的重要关系，需要特别注意：

- `default_model_index` 指定使用某个提供商的哪个模型，索引从 0 开始
- `models` 是一个列表，包含该提供商支持的所有模型名称
- 系统会根据 `default_model_index` 的值从 `models` 列表中选择对应索引的模型

例如：
```yaml
llm:
  provider: "openai"
  default_model_index: 0  # 使用第一个模型
  openai:
    models:
      - "gpt-4-1106-preview"  # 索引 0
      - "gpt-4"               # 索引 1
      - "gpt-3.5-turbo"       # 索引 2
```

在上例中，`default_model_index: 0` 表示使用 "gpt-4-1106-preview" 模型。如果设置为 1，则使用 "gpt-4"。

**注意事项**：
- `default_model_index` 必须是有效的数组索引，不能超出 `models` 列表的范围
- 如果设置了无效的索引值，系统会抛出错误提示：`default_model_index {index} 超出模型列表范围 [0, {len-1}]`

#### 其他重要参数

- `max_requests`: 限制单次会话中最大 API 请求次数，防止意外消耗过多 API 额度
- `api_key`: 各提供商的 API 密钥
- `base_url`: API 服务的基础 URL，可用于自定义 API 端点
- `temperature`: 生成文本的随机性参数，值越高结果越多样
- `max_tokens`: 每次请求的最大 token 数量限制

## VLM 配置

视觉语言模型配置，用于处理包含图像的任务：

```yaml
vlm:
  provider: "openai_siliconflow"
  openai_siliconflow:
    api_key: "your-api-key"
    base_url: "https://api.siliconflow.com/v1"
    models:
      - "Qwen/Qwen2-VL-72B-Instruct"
      - "Qwen/Qwen2-VL-7B-Instruct"
    temperature: 0.7
    max_tokens: 4096
```

## 文档转换器配置

```yaml
document_converter:
  converter_name: "markitdown"  # 可选: markitdown, mineru
```

文档转换器负责将输入文档(如PDF)转换为文本格式，供LLM处理。目前支持两种转换器：
- markitdown: 默认转换器，适用于大多数文档
- mineru: 基于 MinerU 模型的高级转换器，对学术文档结构识别更优

## 输出配置

```yaml
output:
  default_format: "markdown"  # 可选: markdown, csv, folder
  base_path: "outputs/"
  markdown_template: "templates/markdown_template.md"
  csv_columns: ["title", "url", "summary", "methodology", "results", "timestamp"]
```

输出配置控制分析结果的保存方式和格式：
- `default_format`: 默认输出格式
- `base_path`: 输出文件存储的基础路径
- `markdown_template`: Markdown 模板文件路径
- `csv_columns`: CSV 输出时的列名

## 提示词配置

```yaml
prompts:
  file: "config/prompts_llm.yaml"  # 提示词配置文件路径
  default: "summary"  # 默认使用的提示词
  available:
    - summary
    - methodology
    - results
    - contribution
    - full_analysis
```

提示词配置定义了系统使用的各种提示模板：
- `file`: 提示词配置文件路径
- `default`: 默认使用的提示词名称
- `available`: 可用提示词列表

## Agent 配置

```yaml
agent:
  max_iterations: 5  # 最大迭代次数
  timeout: 300  # 超时时间（秒）
  memory_window: 10  # 记忆窗口大小
```

Agent 配置控制智能代理的行为参数：
- `max_iterations`: 单次任务的最大处理迭代次数
- `timeout`: 操作超时时间（秒）
- `memory_window`: 代理记忆上下文的窗口大小

## 配置文件使用注意事项

1. **模型索引的正确设置**：确保 `default_model_index` 的值不超过对应提供商 `models` 列表的长度减 1。

2. **API 密钥保护**：不要在公共环境中暴露配置文件，特别是包含 API 密钥的部分。

3. **模型兼容性**：不同提供商的模型参数（如 max_tokens）可能有所不同，请根据实际模型能力调整。

4. **配置文件路径**：确保配置文件放置在系统预期的位置，通常是项目根目录的 `config` 文件夹中。

5. **提示词文件**：确保 `prompts.file` 指向的提示词配置文件存在且格式正确。

## 配置修改方法

1. 复制 `config.yaml.example` 为 `config.yaml`
2. 根据需要修改配置值
3. 保存文件后重启应用使配置生效

## 错误排查

如果遇到配置相关的错误：
- 检查 YAML 语法是否正确
- 确认必填字段是否都已提供
- 验证 `default_model_index` 是否在有效范围内
- 检查 API 密钥是否正确设置

## 配置示例

完整的配置示例可以参考项目中的 `config/config.yaml.example` 文件。
