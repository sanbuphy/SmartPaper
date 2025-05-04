# SmartPaper 配置系统使用指南

`config.py` 模块提供了一个统一的配置管理系统，支持从 YAML 文件加载配置、动态修改配置并保存到文件。配置系统实现了单例模式，确保在整个应用程序中只有一个配置实例。

## 基本用法

### 初始化配置系统

```python
from SmartPaper.core.config import Config

# 使用默认配置文件路径
config = Config()

# 指定配置文件路径
config = Config(config_path="path/to/config.yaml")

# 通过环境变量指定配置文件路径
# 先设置环境变量 CONFIG_PATH
import os
os.environ["CONFIG_PATH"] = "path/to/config.yaml"
# 然后初始化配置
config = Config()  # 会从环境变量读取路径
```

### 访问配置项

配置系统支持多种方式访问配置项：

```python
# 使用 get 方法获取配置，支持点号分隔的路径和默认值
api_key = config.get("llm.openai.api_key", "")
model = config.get("llm.openai.models", [])[0]
temperature = config.get("llm.openai.temperature", 0.7)

# 使用属性访问特定配置项
provider = config.llm_provider  # 获取当前 LLM 提供商
default_model = config.default_model  # 获取当前默认模型
```

### 修改配置

```python
# 使用 set 方法修改配置，支持点号分隔的路径
config.set("llm.openai.temperature", 0.8)

# 使用属性设置特定配置项
config.llm_provider = "openai_siliconflow"
config.temperature = 0.9
config.max_tokens = 8192

# 批量更新多个配置项
config.update({
    "llm.provider": "openai",
    "llm.openai.temperature": 0.7,
    "llm.openai.max_tokens": 4096
})
```

### 保存配置到文件

```python
# 手动保存所有配置到文件
config.save()

# 修改配置时自动保存
config.set("llm.max_requests", 20, auto_save=True)

# 批量更新配置时自动保存
config.update({
    "llm.provider": "openai",
    "llm.openai.api_key": "your-api-key"
}, auto_save=True)
```

## 配置文件格式

配置文件采用 YAML 格式，示例如下：

```yaml
llm:
  provider: openai_siliconflow  # 默认 LLM 提供商
  max_requests: 10              # 最大请求次数
  default_model_index: 0        # 默认模型索引
  
  openai_siliconflow:           # 提供商配置
    api_key: "your-api-key"     # API 密钥
    base_url: "https://api.siliconflow.com/v1"  # API 基础 URL
    models:                      # 可用模型
      - "Qwen/Qwen2.5-7B-Instruct" 
    temperature: 0.7            # 默认温度
    max_tokens: 4096            # 默认最大生成 token 数
    
  openai:                       # 另一个提供商
    api_key: "your-openai-key"
    models:
      - "gpt-4-1106-preview"
      - "gpt-4"
      - "gpt-3.5-turbo"
    temperature: 0.7
    max_tokens: 2048
    
document_converter:
  converter_name: "fitz_with_image"  # 文档转换器名称
```

## 特定配置项访问

### LLM 提供商配置

```python
# 获取/设置当前 LLM 提供商
provider = config.llm_provider
config.llm_provider = "openai"

# 获取当前 LLM 提供商的配置
provider_config = config.llm_config

# 获取/设置 API 密钥
api_key = config.api_key
config.api_key = "your-api-key"

# 为特定提供商设置 API 密钥和基础 URL
config.set_provider_api_key("openai_siliconflow", "new-siliconflow-key")
config.set_provider_base_url("openai_siliconflow", "https://api.siliconflow.com/v1")

# 获取/设置基础 URL
base_url = config.base_url
config.base_url = "https://api.siliconflow.com/v1"
```

### 模型配置

```python
# 获取当前提供商的可用模型列表
models = config.models

# 添加/删除模型
config.add_model("gpt-4", "openai")
config.remove_model("gpt-3.5-turbo", "openai")

# 获取/设置默认模型索引
default_index = config.default_model_index
config.default_model_index = 1

# 获取当前默认模型
default_model = config.default_model
```

### 其他配置项

```python
# 温度参数
temperature = config.temperature
config.temperature = 0.8

# 最大 token 数
max_tokens = config.max_tokens
config.max_tokens = 4096

# 最大请求次数
max_requests = config.max_requests
config.max_requests = 20

# 文档转换器
converter = config.document_converter
config.document_converter = "fitz_with_image"
```

## 配置文件自动查找

当未指定配置文件路径时，系统会按以下顺序查找配置文件：

1. `SmartPaper/config_files/config.yaml`
2. 当前工作目录下的 `config.yaml`
3. `SmartPaper/core/config.yaml`

如果找不到配置文件，系统会创建一个默认配置并保存到第一个查找路径。

## 单例模式

`Config` 类实现了单例模式，确保在整个应用程序中只有一个配置实例。这意味着，无论您在应用的哪个部分创建 `Config` 实例，都会得到相同的配置对象。

```python
# 在不同模块中
config1 = Config()
config2 = Config()

# config1 和 config2 是同一个对象
assert config1 is config2
```

但是，如果您传入了不同的配置文件路径，单例会使用新的路径重新加载配置：

```python
config1 = Config("path1.yaml")
config2 = Config("path2.yaml")  # 会重新加载 path2.yaml 的配置

# 它们仍是同一个对象，但配置内容已更新
assert config1 is config2
# config1 的路径也会更新为 path2.yaml
print(config1.config_path)  # 输出: path2.yaml
```

## 应用场景示例

### 管理多个 LLM 服务

```python
from SmartPaper.core.config import Config

config = Config()

# 添加新的提供商
config.set("llm.zhipu", {
    "api_key": "your-zhipu-key",
    "base_url": "https://api.zhipuai.cn/v1",
    "models": ["glm-4", "glm-3-turbo"],
    "temperature": 0.7,
    "max_tokens": 2048
})
config.save()

# 切换到新提供商
config.llm_provider = "zhipu"
```

### 创建配置 UI

```python
import tkinter as tk
from SmartPaper.core.config import Config

class ConfigUI:
    def __init__(self, master):
        self.master = master
        self.config = Config()
        
        # 创建 UI 组件
        self.provider_label = tk.Label(master, text="LLM 提供商:")
        self.provider_var = tk.StringVar(value=self.config.llm_provider)
        self.provider_menu = tk.OptionMenu(master, self.provider_var, "openai", "openai_siliconflow")
        self.provider_var.trace("w", self.update_provider)
        
        self.api_key_label = tk.Label(master, text="API 密钥:")
        self.api_key_var = tk.StringVar(value=self.config.api_key)
        self.api_key_entry = tk.Entry(master, textvariable=self.api_key_var, width=40)
        
        self.save_button = tk.Button(master, text="保存配置", command=self.save_config)
        
        # 布局 UI 组件
        self.provider_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.provider_menu.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.api_key_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.api_key_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.save_button.grid(row=2, column=1, sticky="e", padx=5, pady=10)
    
    def update_provider(self, *args):
        provider = self.provider_var.get()
        self.config.llm_provider = provider
        self.api_key_var.set(self.config.api_key)
    
    def save_config(self):
        provider = self.provider_var.get()
        api_key = self.api_key_var.get()
        
        self.config.llm_provider = provider
        self.config.api_key = api_key
        self.config.save()
        tk.messagebox.showinfo("成功", "配置已保存")

# 创建应用
root = tk.Tk()
root.title("SmartPaper 配置")
app = ConfigUI(root)
root.mainloop()
```