# SmartPaper API 文档

## 概述

SmartPaper API提供了一系列端点，用于处理学术论文的下载、解析和智能问答。API支持从arXiv下载论文、上传本地PDF文件，以及使用各种大语言模型与论文内容进行对话。

## 基础API

### 论文对话

#### 与arXiv论文对话

```http
POST /chat_with_arxiv
```

从arXiv下载论文并与之对话。

**请求参数**:

| 参数名 | 类型 | 必选 | 描述 |
|---|---|---|---|
| paper_id | string | 是 | arXiv论文ID |
| task_type | string | 是 | 任务类型，如"coolpapaers", "yuanbao", "methodology"等 |
| provider | string | 否 | LLM提供商（如openai, openai_siliconflow等） |
| model | string | 否 | 模型名称 |
| image_text_mode | boolean | 否 | 是否启用图文模式，提取论文图片 |
| use_cache | boolean | 否 | 是否使用缓存 |
| stream | boolean | 否 | 是否使用流式输出（此端点仅支持false） |
| force_download | boolean | 否 | 是否强制重新下载论文 |

**响应**:

```json
{
  "response": "模型回复内容",
  "success": true,
  "paper_metadata": null,
  "error": null
}
```

#### 与arXiv论文流式对话

```http
POST /chat_with_arxiv_stream
```

从arXiv下载论文并进行流式对话，使用服务器发送事件(SSE)进行流式响应。

**请求参数**:
与 `/chat_with_arxiv` 相同，但必须设置 `stream=true`。

**响应**:
以SSE格式流式返回模型回复。

#### 与本地论文对话

```http
POST /chat_with_local
```

与已上传或本地的PDF论文文件对话。

**请求参数**:

| 参数名 | 类型 | 必选 | 描述 |
|---|---|---|---|
| pdf_path | string | 是 | PDF文件的本地路径 |
| task_type | string | 是 | 任务类型 |
| provider | string | 否 | LLM提供商 |
| model | string | 否 | 模型名称 |
| image_text_mode | boolean | 否 | 是否启用图文模式 |
| use_cache | boolean | 否 | 是否使用缓存 |
| stream | boolean | 否 | 是否使用流式输出（此端点仅支持false） |

**响应**:
与 `/chat_with_arxiv` 相同。

#### 与本地论文流式对话

```http
POST /chat_with_local_stream
```

与本地论文进行流式对话。

**请求参数**:
与 `/chat_with_local` 相同，但必须设置 `stream=true`。

**响应**:
以SSE格式流式返回模型回复。

### 论文管理

#### 上传论文

```http
POST /upload_paper
```

上传PDF论文文件。

**请求参数**:
使用 `multipart/form-data` 格式，文件字段名为 `file`。

**响应**:

```json
{
  "file_id": "唯一文件ID",
  "file_path": "文件保存路径",
  "success": true,
  "error": null
}
```

#### 列出已上传的论文

```http
GET /list_uploaded_papers
```

列出所有已上传的论文文件。

**请求参数**: 无

**响应**:

```json
{
  "success": true,
  "files": [
    {
      "file_id": "文件ID",
      "file_name": "文件名",
      "file_path": "文件路径",
      "size_bytes": 文件大小
    }
  ],
  "error": null
}
```

### 配置管理

#### 获取配置信息

```http
GET /config
```

获取系统配置信息，包括可用的模型和提供商。

**请求参数**: 无

**响应**:

```json
{
  "providers": [
    {
      "name": "提供商名称",
      "models": [
        {
          "name": "模型名称",
          "context_length": 模型上下文长度
        }
      ],
      "base_url": "API基础URL",
      "temperature": 温度值,
      "max_tokens": 最大token数
    }
  ],
  "default_provider": "默认提供商",
  "default_model": "默认模型",
  "success": true,
  "error": null
}
```

#### 更新配置信息

```http
POST /config
```

更新系统配置。

**请求参数**:

```json
{
  "provider": "提供商名称",
  "model": "模型名称",
  "api_key": "API密钥",
  "base_url": "API基础URL",
  "temperature": 温度值,
  "max_tokens": 最大token数
}
```

**响应**:
与 GET `/config` 相同，返回更新后的配置。

#### 重新加载配置

```http
POST /config/reload
```

从配置文件重新加载系统配置。

**请求参数**: 无

**响应**:

```json
{
  "success": true,
  "error": null
}
```

#### 列出所有模型

```http
GET /models
```

获取所有可用模型的列表。

**请求参数**: 无

**响应**:

```json
{
  "models": [
    {
      "provider": "提供商名称",
      "name": "模型名称",
      "context_length": 上下文长度
    }
  ],
  "default_provider": "默认提供商",
  "default_model": "默认模型",
  "success": true,
  "error": null
}
```

## 提示词管理API

所有提示词API的基础路径为 `/api/v1/prompts`。

### 获取提示词列表

```http
GET /api/v1/prompts/list
```

获取所有可用的提示词。

**请求参数**:

| 参数名 | 类型 | 必选 | 描述 |
|---|---|---|---|
| prompt_type | string | 否 | 提示词类型过滤器，如"llm"或"llm_with_image" |

**响应**:

```json
{
  "prompts": {
    "llm": ["coolpapaers", "yuanbao", "methodology"],
    "llm_with_image": ["coolpapaers", "yuanbao"]
  },
  "success": true,
  "error": null
}
```

### 获取提示词详情

```http
GET /api/v1/prompts/detail/{prompt_type}/{prompt_name}
```

获取特定提示词的详细信息。

**请求参数**:

| 参数名 | 类型 | 必选 | 描述 |
|---|---|---|---|
| prompt_type | string | 是 | 提示词类型，如"llm"或"llm_with_image" |
| prompt_name | string | 是 | 提示词名称 |

**响应**:

```json
{
  "template": "提示词模板内容",
  "description": "提示词描述",
  "success": true,
  "error": null
}
```

### 更新或创建提示词

```http
POST /api/v1/prompts/update
```

更新现有提示词或创建新提示词。

**请求参数**:

```json
{
  "prompt_type": "提示词类型",
  "prompt_name": "提示词名称",
  "template": "提示词模板内容",
  "description": "提示词描述"
}
```

**响应**:

```json
{
  "success": true,
  "error": null
}
```

### 删除提示词

```http
POST /api/v1/prompts/delete
```

删除指定的提示词。

**请求参数**:

```json
{
  "prompt_type": "提示词类型",
  "prompt_name": "提示词名称"
}
```

**响应**:

```json
{
  "success": true,
  "error": null
}
```

### 重新加载提示词

```http
POST /api/v1/prompts/reload
```

从配置文件重新加载所有提示词。

**请求参数**: 无

**响应**:

```json
{
  "success": true,
  "error": null
}
```

### 获取任务类型列表

```http
GET /api/v1/prompts/task_types
```

获取所有可用的任务类型。

**请求参数**: 无

**响应**:

```json
{
  "task_types": ["coolpapaers", "yuanbao", "methodology", ...],
  "success": true,
  "error": null
}
```

### 获取任务类型描述

```http
GET /api/v1/prompts/task_descriptions
```

获取所有任务类型的描述信息。

**请求参数**: 无

**响应**:

```json
{
  "descriptions": {
    "coolpapaers": "复刻 papers.cool",
    "yuanbao": "类似混元元宝总结",
    "methodology": "研究方法论分析"
  },
  "success": true,
  "error": null
}
```

## 错误处理

所有API端点在发生错误时会返回带有错误信息的JSON响应。

常见错误状态码:

- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

错误响应示例:

```json
{
  "success": false,
  "error": "错误详情描述"
}
```

## 使用示例

### 与arXiv论文对话

```python
import requests

url = "http://localhost:8000/chat_with_arxiv"
payload = {
    "paper_id": "2303.08774",
    "task_type": "coolpapaers",
    "provider": "openai_siliconflow",
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "image_text_mode": true,
    "use_cache": true,
    "stream": false
}
response = requests.post(url, json=payload)
print(response.json())
```

### 上传论文文件

```python
import requests

url = "http://localhost:8000/upload_paper"
files = {"file": open("paper.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```