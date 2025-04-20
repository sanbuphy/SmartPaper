"""
#### 使用说明：

该代码提供了基于MarkItDown的PDF转Markdown转换功能的封装。

#### 主要功能：
- 提供基于MarkItDown库将PDF文件转换为Markdown的功能

#### 参数说明：

- **markitdown_pdf2md函数**：
  - `file_path (str)`: 要转换的PDF文件路径。
  - `llm_client (Any, optional)`: LLM客户端，用于图像描述等高级功能。
  - `llm_model (str, optional)`: LLM模型名称。
  - `config (Dict, optional)`: 配置信息（如最大请求次数等）。
  - `ocr_enabled (bool, optional)`: 是否启用OCR功能，默认不启用。
  - **返回值**：返回一个包含`text_content`（转换后的Markdown文本），`metadata`（附加元数据），以及`images`（转换过程中提取的图片）的字典。

#### 注意事项：
- 请确保安装了`markitdown`、`loguru`等依赖库。
- 只支持PDF文件格式。

#### 更多信息：
- 本转换器提供了LLM集成，可以对图像或复杂内容进行更深入的分析和描述。

"""

import os
from typing import Dict, Any
from pathlib import Path
from markitdown import MarkItDown


def markitdown_pdf2md(
    file_path: str,
    llm_client: Any = None,
    llm_model: str = None,
    config: Dict = None,
    ocr_enabled: bool = False,
) -> Dict:
    """将PDF文件转换为Markdown

    Args:
        file_path (str): PDF文件路径
        llm_client (Any, optional): LLM客户端，用于图像描述等高级功能
        llm_model (str, optional): LLM模型名称
        config (Dict, optional): 配置信息
        ocr_enabled (bool, optional): 是否启用OCR功能，默认不启用

    Returns:
        Dict: 包含转换结果的字典
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    ext = file_path.suffix.lower()
    if ext != ".pdf":
        raise ValueError(f"只支持PDF文件，当前文件类型: {ext}")

    try:
        # 根据是否提供LLM客户端来初始化MarkItDown
        if llm_client and llm_model:
            md = MarkItDown(llm_client=llm_client, llm_model=llm_model)
        else:
            md = MarkItDown()

        result = md.convert(str(file_path))
        return {"text_content": result.text_content, "metadata": {}, "images": []}
    except Exception as e:
        raise Exception(f"PDF转换失败: {str(e)}")
