# 注册新的文档转换器

SmartPaper支持用户自定义和注册文档转换器，使系统能够处理更多类型的文档格式或使用不同的转换算法。本文档详细说明了如何创建和注册自己的文档转换器。

## 文档转换器概述

文档转换器是将各种格式的文档（例如PDF、Word等）转换为系统可处理的文本格式的模块。SmartPaper使用统一的注册机制管理这些转换器，便于扩展和切换不同的转换器。

目前系统默认支持的转换器包括：
- `markitdown`：基于MarkItDown库的PDF转Markdown转换器（默认）
- `mineru`：基于MinerU的PDF转Markdown转换器

## 创建新的转换器

### 1. 转换器函数规范

要创建新的转换器，需要实现一个符合以下接口规范的函数：

```python
def your_converter_function(
    file_path: str,  # 文件路径
    llm_client: Any = None,  # LLM客户端（可选）
    llm_model: str = None,  # LLM模型名称（可选）
    config: Dict = None,  # 配置信息（可选）
    **kwargs  # 其他可选参数
) -> Dict:
    """
    文档转换函数

    Args:
        file_path: 要转换的文件路径
        llm_client: LLM客户端，用于图像描述等高级功能（可选）
        llm_model: LLM模型名称（可选）
        config: 配置信息（可选）
        **kwargs: 其他可选参数

    Returns:
        Dict: 包含以下键的字典：
            - text_content: 转换后的文本内容
            - metadata: 文档元数据（如标题、作者等）
            - images: 提取的图像列表（可选）
    """
    # 实现转换逻辑...

    return {
        "text_content": "转换后的文本内容",
        "metadata": {"title": "文档标题", "author": "作者", ...},
        "images": [...]  # 可选
    }
```

### 2. 转换器实现示例

下面是一个简单的转换器示例，用于将TXT文件转换为系统可处理的格式：

```python
# src/tools/everything_to_text/txt_to_md.py

"""
#### 使用说明：
该模块用于将TXT文件转换为系统可处理的格式。

#### 主要功能：
1. 读取TXT文件并提取内容
2. 分析文件结构并提取潜在的标题和段落
3. 返回结构化的文本内容

#### 参数说明：
- file_path (str): TXT文件路径
- llm_client (Any, optional): LLM客户端
- llm_model (str, optional): LLM模型名称
- config (Dict, optional): 配置信息
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


def txt_to_md(
    file_path: str,
    llm_client: Any = None,
    llm_model: str = None,
    config: Dict = None,
) -> Dict:
    """将TXT文件转换为结构化格式

    Args:
        file_path (str): TXT文件路径
        llm_client (Any, optional): LLM客户端
        llm_model (str, optional): LLM模型名称
        config (Dict, optional): 配置信息

    Returns:
        Dict: 包含转换结果的字典
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    ext = file_path.suffix.lower()
    if ext != ".txt":
        raise ValueError(f"只支持TXT文件，当前文件类型: {ext}")

    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取文件名作为标题
        title = file_path.stem

        # 转换为markdown格式
        md_content = f"# {title}\n\n{content}"

        # 返回结果
        return {
            "text_content": md_content,
            "metadata": {"title": title},
            "images": []
        }
    except Exception as e:
        raise Exception(f"TXT文件转换失败: {str(e)}")
```

## 注册新的转换器

### 1. 修改注册文件

创建完转换器函数后，需要在`src/core/register_converters.py`文件中注册这个转换器：

```python
# src/core/register_converters.py

"""注册所有文档转换器

这个模块负责注册所有可用的文档转换器。
新的转换器应该在这里注册。
"""

from pathlib import Path
from typing import Dict, Any, Optional
from .document_converter import DocumentConverter

# 导入所有转换器
try:
    from tools.everything_to_text.pdf_to_md_mineru import mineru_pdf2md
    _has_mineru = True
except ImportError:
    _has_mineru = False

try:
    from tools.everything_to_text.pdf_to_md_markitdown import markitdown_pdf2md
    _has_markitdown = True
except ImportError:
    _has_markitdown = False

# 导入你的新转换器
try:
    from tools.everything_to_text.txt_to_md import txt_to_md
    _has_txt_converter = True
except ImportError:
    _has_txt_converter = False


def register_all_converters():
    """注册所有可用的转换器"""
    # 注册 MarkItDown 转换器（作为默认PDF转换器）
    if _has_markitdown:
        DocumentConverter.register("markitdown", markitdown_pdf2md)

    # 注册 Mineru 转换器
    if _has_mineru:
        DocumentConverter.register("mineru", mineru_pdf2md)

    # 注册你的新转换器
    if _has_txt_converter:
        DocumentConverter.register("txt_converter", txt_to_md)

    # 在这里添加更多转换器的注册...


# 在模块导入时自动注册所有转换器
register_all_converters()
```

### 2. 使用新注册的转换器

注册完成后，可以通过以下方式使用新转换器：

```python
from core.document_converter import convert_to_text

# 使用特定转换器处理文件
result = convert_to_text("path/to/your/file.txt", converter_name="txt_converter")

# 输出转换后的内容
print(result["text_content"])
```

也可以在配置文件中设置默认使用的转换器：

```yaml
document_converter:
  converter_name: "txt_converter"
```

## 转换器的高级功能

### 1. 利用LLM增强功能

如果你的转换器需要利用LLM来增强功能（如图像描述、复杂表格理解等），可以在转换函数中使用传入的`llm_client`和`llm_model`：

```python
def advanced_converter(
    file_path: str,
    llm_client: Any = None,
    llm_model: str = None,
    config: Dict = None,
) -> Dict:
    # 基本转换逻辑...

    # 如果提供了LLM客户端，可以使用它来增强功能
    if llm_client and llm_model:
        # 例如，使用LLM描述图像
        image_description = get_image_description(image_path, llm_client, llm_model)
        # 将描述添加到内容中...

    return {...}
```

### 2. 处理配置信息

使用传入的`config`字典获取配置信息：

```python
def configurable_converter(
    file_path: str,
    llm_client: Any = None,
    llm_model: str = None,
    config: Dict = None,
) -> Dict:
    config = config or {}

    # 获取特定于此转换器的配置
    converter_config = config.get("your_converter_name", {})

    # 使用配置参数
    option1 = converter_config.get("option1", "default_value")
    option2 = converter_config.get("option2", True)

    # 转换逻辑...

    return {...}
```

## 测试转换器

建议为新的转换器创建测试，以确保其功能正确：

```python
# tests/tools/test_txt_converter.py

import pytest
import os
import sys
from typing import Dict



from core.document_converter import convert_to_text

def test_txt_converter():
    """测试TXT文件转换器"""
    # 准备测试文件
    test_file = "tests/data/sample.txt"

    # 使用转换器
    result = convert_to_text(test_file, converter_name="txt_converter")

    # 验证结果
    assert isinstance(result, Dict)
    assert "text_content" in result
    assert "metadata" in result
    assert "title" in result["metadata"]
```

## 最佳实践

1. **命名约定**：将转换器函数和文件名保持一致性，例如`txt_to_md.py`中定义`txt_to_md`函数。

2. **异常处理**：确保转换器中有适当的错误处理，以防止因文件格式不支持或读取失败而导致的崩溃。

3. **文档化**：为你的转换器提供详细的文档字符串，说明其功能、参数和返回值。

4. **可选依赖**：如果你的转换器依赖于第三方库，确保在`register_converters.py`中使用`try/except`处理导入失败的情况。

5. **配置灵活性**：设计你的转换器时考虑配置的灵活性，允许用户通过配置文件调整转换行为。

通过遵循上述指南，你可以轻松地为SmartPaper系统添加新的文档转换器，扩展其功能以支持更多类型的文档或使用不同的转换算法。
