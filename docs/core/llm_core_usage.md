# SmartPaper LLM 核心模块使用指南

`llm_core.py` 模块提供了 OpenAI 兼容接口的 LLM 调用基础功能，支持单轮对话、多轮对话和流式输出。作为 SmartPaper 的基础模块，它被 `chat_model_manager.py` 调用以实现更高级的功能。

## OpenAILLM 类

`OpenAILLM` 是核心类，负责与 OpenAI 兼容 API 的通信。它支持：

- 标准 OpenAI API
- 具有 OpenAI 兼容接口的第三方服务（如硅基流、智谱 AI 等）

### 初始化

```python
from SmartPaper.core.llm_core import OpenAILLM

# 基本初始化
llm = OpenAILLM(
    api_key="your-api-key",
    model="gpt-3.5-turbo"
)

# 完整初始化
llm = OpenAILLM(
    api_key="your-api-key",
    model="gpt-3.5-turbo",
    base_url="https://api.siliconflow.com/v1",  # 第三方 API URL
    temperature=0.7,  # 控制输出随机性 (0-2)
    max_tokens=2048   # 最大生成 token 数
)
```

API 密钥和基础 URL 可以通过环境变量设置：
- `OPENAI_API_KEY`: API 密钥
- `OPENAI_API_BASE`: API 基础 URL

## 基本用法

### 单轮对话

```python
# 无流式输出
response = llm.chat(
    message="你好，请介绍一下自己",
    system_prompt="你是一个简洁、友好的AI助手"
)
print(f"模型响应:\n{response}")

# 流式输出（返回迭代器）
for chunk in llm.chat(
    message="给我讲个简短的故事",
    system_prompt="你是一个创意故事讲述者",
    stream=True
):
    print(chunk, end="", flush=True)
```

### 多轮对话

```python
# 准备对话历史
messages = [
    {"role": "system", "content": "你是一个帮助用户学习Python编程的助手，提供简洁明了的回答。"},
    {"role": "user", "content": "什么是Python装饰器？"},
    {"role": "assistant", "content": "Python装饰器是一种函数，它接受另一个函数并扩展该函数的行为而不明确修改它的代码。"},
    {"role": "user", "content": "能给我一个简单的装饰器例子吗？"}
]

# 无流式输出
response = llm.chat_with_history(messages=messages)
print(f"模型响应:\n{response}")

# 流式输出（返回迭代器）
for chunk in llm.chat_with_history(messages=messages, stream=True):
    print(chunk, end="", flush=True)
```

### 使用回调函数处理流式输出

```python
# 定义回调函数处理流式输出
def print_chunk(chunk: str):
    print(chunk, end="", flush=True)

# 单轮对话流式输出
llm.stream_callback(
    message="给我讲个简短的故事",
    callback=print_chunk,
    system_prompt="你是一个创意故事讲述者"
)

# 多轮对话流式输出
llm.stream_with_history_callback(
    messages=messages,
    callback=print_chunk
)
```

## 便捷函数

模块提供了一系列便捷函数，无需创建 `OpenAILLM` 实例：

### 单次回复

```python
from SmartPaper.core.llm_core import get_llm_response

# 基本用法
response = get_llm_response(
    message="你好，请介绍一下你自己",
    api_key="your-api-key",
    model="gpt-3.5-turbo"
)
print(f"模型响应:\n{response}")

# 流式输出
for chunk in get_llm_response(
    message="给我讲个简短的故事",
    system_prompt="你是一个创意故事讲述者",
    api_key="your-api-key",
    model="gpt-3.5-turbo",
    base_url="https://api.siliconflow.com/v1",
    stream=True,
    temperature=0.8,
    max_tokens=1024
):
    print(chunk, end="", flush=True)
```

### 使用回调函数

```python
from SmartPaper.core.llm_core import get_llm_response_with_callback

def print_chunk(chunk: str):
    print(chunk, end="", flush=True)

# 单轮对话
get_llm_response_with_callback(
    message="给我讲个简短的故事",
    callback=print_chunk,
    system_prompt="你是一个创意故事讲述者",
    api_key="your-api-key",
    model="gpt-3.5-turbo"
)
```

### 使用对话历史和回调函数

```python
from SmartPaper.core.llm_core import get_llm_response_with_history_callback

messages = [
    {"role": "system", "content": "你是一个帮助用户学习Python编程的助手"},
    {"role": "user", "content": "什么是Python装饰器？"},
    {"role": "assistant", "content": "Python装饰器是一种函数..."},
    {"role": "user", "content": "能给我一个简单的装饰器例子吗？"}
]

def print_chunk(chunk: str):
    print(chunk, end="", flush=True)

get_llm_response_with_history_callback(
    messages=messages,
    callback=print_chunk,
    api_key="your-api-key",
    model="gpt-3.5-turbo"
)
```

## 错误处理

常见错误及解决方案：

1. **API 密钥错误**：确保提供了有效的 API 密钥
   ```python
   # 错误提示: ValueError: 未提供OpenAI API密钥
   # 解决方法: 提供 API 密钥
   llm = OpenAILLM(api_key="your-api-key")
   ```

2. **连接错误**：检查网络和 API 基础 URL
   ```python
   # 连接报错时，检查 base_url 是否正确
   llm = OpenAILLM(
       api_key="your-api-key",
       base_url="https://correct-api-domain.com/v1"
   )
   ```

3. **模型不可用**：确认选择的模型名称在对应 API 中可用
   ```python
   # 如果使用的是硅基流，确保模型名称正确
   llm = OpenAILLM(
       api_key="your-api-key",
       base_url="https://api.siliconflow.com/v1",
       model="Qwen/Qwen2.5-7B-Instruct"  # 正确的模型名
   )
   ```

## 与高级模块集成

`llm_core.py` 通常作为底层模块被 `chat_model_manager.py` 调用，除特殊需求外，建议使用 `chat_model_manager.py` 提供的更完整功能：

```python
# 推荐：使用 ModelManager
from SmartPaper.core.chat_model_manager import ModelManager
manager = ModelManager()
response = manager.chat("你好")

# 特殊情况：直接使用 OpenAILLM
from SmartPaper.core.llm_core import OpenAILLM
llm = OpenAILLM(api_key="your-key", model="your-model")
response = llm.chat("你好")
```

## 扩展开发

如果需要支持新的 LLM API 格式，您可以参照 `OpenAILLM` 类的接口创建新的 LLM 类：

```python
class CustomLLM:
    def __init__(self, api_key, model, **kwargs):
        # 初始化代码...
        
    def chat(self, message, system_prompt="You are a helpful assistant.", stream=False):
        # 实现聊天功能...
        
    def chat_with_history(self, messages, stream=False):
        # 实现带历史的聊天功能...
        
    # 实现其他必要的方法...
```

然后，您可以将其注册到 `ModelManager`：

```python
from SmartPaper.core.chat_model_manager import ModelManager
manager = ModelManager()
manager.register_provider("custom_provider", CustomLLM)
```