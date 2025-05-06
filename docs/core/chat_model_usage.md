# SmartPaper 聊天模型管理器使用指南

`chat_model_manager.py` 模块提供了统一的 LLM 调用管理接口，支持多种模型和提供商，并集成了配置系统，让您可以方便地在不同的 LLM 服务之间切换。

## 基本概念

- **ModelManager**: 核心类，负责管理 LLM 服务提供商和模型
- **提供商(Provider)**: 如 OpenAI、硅基流等 LLM API 提供商
- **模型(Model)**: 提供商提供的具体模型，如 GPT-4、Qwen2.5-7B-Instruct 等

## 配置系统

模块首先会尝试加载配置文件（默认为 `config.yaml`），配置示例：

```yaml
llm:
  provider: openai_siliconflow  # 默认提供商
  max_requests: 10
  default_model_index: 0
  openai_siliconflow:          # 提供商配置
    api_key: "your-api-key"    # API 密钥
    base_url: "https://api.siliconflow.com/v1"  # API 基础 URL
    models:                     # 可用模型
      - "Qwen/Qwen2.5-7B-Instruct"
    temperature: 0.7
    max_tokens: 4096
  openai:                      # 另一个提供商
    api_key: "your-openai-key"
    models:
      - "gpt-4-1106-preview"
      - "gpt-4"
      - "gpt-3.5-turbo"
    temperature: 0.7
    max_tokens: 2048
```

## 基本用法

### 初始化模型管理器

```python
from SmartPaper.core.chat_model_manager import ModelManager

# 使用默认配置文件
manager = ModelManager()

# 或指定配置文件路径
manager = ModelManager(config_path="path/to/config.yaml")
```

### 列出可用提供商和模型

```python
# 列出可用的 LLM 提供商
providers = manager.list_available_providers()
print(f"可用的 LLM 提供商: {providers}")

# 列出特定提供商的可用模型
models = manager.list_available_models("openai_siliconflow")
print(f"提供商 openai_siliconflow 的可用模型: {models}")
```

### 单轮对话

```python
# 使用默认提供商和模型
response = manager.chat(
    message="你好，请介绍一下你自己",
    system_prompt="你是一个简洁、友好的AI助手"
)
print(f"模型响应:\n{response}")

# 指定提供商和模型
response = manager.chat(
    message="请简要总结一下大语言模型的工作原理",
    system_prompt="你是一个简洁、专业的AI助手",
    provider="openai",
    model="gpt-4"
)
print(f"模型响应:\n{response}")
```

### 多轮对话（使用对话历史）

```python
messages = [
    {"role": "system", "content": "你是一个帮助用户学习Python编程的助手，提供简洁明了的回答。"},
    {"role": "user", "content": "什么是Python装饰器？"},
    {"role": "assistant", "content": "Python装饰器是一种函数，它接受另一个函数并扩展该函数的行为而不明确修改它的代码。"},
    {"role": "user", "content": "能给我一个简单的装饰器例子吗？"}
]

response = manager.chat_with_history(messages=messages)
print(f"模型响应:\n{response}")
```

### 流式输出

```python
# 定义回调函数处理流式输出
def stream_callback(chunk: str):
    print(chunk, end="", flush=True)

# 单轮对话流式输出
manager.stream_callback(
    message="给我讲个简短的故事",
    callback=stream_callback,
    system_prompt="你是一个创意故事讲述者"
)

# 多轮对话流式输出
manager.stream_with_history_callback(
    messages=messages,
    callback=stream_callback
)
```

## 便捷函数

模块提供了一系列便捷函数，无需创建 `ModelManager` 实例：

```python
from SmartPaper.core.chat_model_manager import chat, chat_with_history
from SmartPaper.core.chat_model_manager import list_available_providers, list_available_models

# 列出可用提供商
providers = list_available_providers()

# 列出可用模型
models = list_available_models("openai_siliconflow")

# 单轮对话
response = chat(
    message="说一个编程的小技巧",
    system_prompt="你是一个专业的编程导师",
    provider="openai_siliconflow",
    model="Qwen/Qwen2.5-7B-Instruct"
)
```

## 高级用法

### 注册新的提供商

如果需要支持新的 LLM 提供商，可以通过 `register_provider` 方法注册：

```python
from SmartPaper.core.llm_core import CustomLLMClass

# 注册新的提供商类
manager.register_provider("custom_provider", CustomLLMClass)
```

### 缓存管理

模块会缓存创建的 LLM 实例以提高性能，如果需要清除缓存：

```python
# 清除所有 LLM 实例缓存
manager.clear_cache()
```

## 错误处理

常见错误及解决方案：

1. API 密钥错误: 检查配置文件中的 API 密钥是否正确
2. 不支持的提供商: 确认提供商名称正确且已在配置文件中定义
3. 连接错误: 检查网络连接和 API 基础 URL 是否正确
4. 模型不可用: 确认选择的模型在对应提供商中可用

## 示例：集成到应用中

```python
import tkinter as tk
from SmartPaper.core.chat_model_manager import ModelManager

class ChatApp:
    def __init__(self):
        self.manager = ModelManager()
        # 应用初始化...
        
    def send_message(self):
        user_message = self.input_field.get()
        
        def update_ui(chunk):
            self.chat_display.insert(tk.END, chunk)
            self.chat_display.see(tk.END)
        
        self.manager.stream_callback(
            message=user_message,
            callback=update_ui,
            system_prompt="你是一个友好的AI助手"
        )
```