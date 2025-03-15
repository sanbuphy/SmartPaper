"""SmartPaper - FastAPI Backend

提供Web API接口，支持论文分析功能
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import os
import re
from src.core.reader import SmartPaper
from src.core.prompt_library import list_prompts
from typing import Dict, AsyncGenerator
import uuid

app = FastAPI(
    title="SmartPaper API",
    description="SmartPaper论文分析API接口",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置日志
logger.add(
    "logs/api.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

def validate_and_format_arxiv_url(url: str) -> str:
    """验证并格式化arXiv URL

    将abs格式转换为pdf格式，并验证URL格式

    Args:
        url: 输入的arXiv URL

    Returns:
        格式化后的URL

    Raises:
        ValueError: 如果URL格式不正确
    """
    logger.debug(f"验证URL格式: {url}")
    # 检查是否是arXiv URL
    arxiv_pattern = r"https?://arxiv\.org/(abs|pdf)/(\d+\.\d+)(v\d+)?"
    match = re.match(arxiv_pattern, url)

    if not match:
        logger.warning(f"URL格式不正确: {url}")
        raise ValueError("URL格式不正确，请提供有效的arXiv URL")

    # 提取arXiv ID
    arxiv_id = match.group(2)
    version = match.group(3) or ""

    # 确保使用PDF格式
    formatted_url = f"https://arxiv.org/pdf/{arxiv_id}{version}"

    if match.group(1) == "abs":
        logger.info(f"URL格式已从abs转换为pdf: {url} -> {formatted_url}")
    else:
        logger.debug(f"URL格式已验证: {formatted_url}")

    return formatted_url

async def process_paper_stream(url: str, prompt_name: str = "yuanbao") -> AsyncGenerator[str, None]:
    """处理论文并以流式方式yield结果"""
    try:
        # 验证并格式化URL
        url = validate_and_format_arxiv_url(url)
        logger.info(f"使用提示词模板: {prompt_name}")
        logger.info(f"处理URL: {url}")

        # 创建输出目录及输出文件
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        session_id = str(uuid.uuid4())
        output_file = os.path.join(
            output_dir, f'analysis_{session_id}_{url.split("/")[-1]}_prompt_{prompt_name}.md'
        )
        logger.info(f"输出文件将保存至: {output_file}\n")

        # 初始化SmartPaper
        logger.debug("初始化SmartPaper")
        reader = SmartPaper(output_format="markdown")

        # 以写入模式打开文件，覆盖旧内容
        logger.debug(f"开始流式处理论文: {url}")
        with open(output_file, "w", encoding="utf-8") as f:
            chunk_count = 0
            total_length = 0
            async for chunk in reader.process_paper_url_stream(
                url, mode="prompt", prompt_name=prompt_name
            ):
                chunk_count += 1
                total_length += len(chunk)
                f.write(chunk)
                if chunk_count % 10 == 0:  # 每10个块记录一次日志
                    logger.debug(f"已接收 {chunk_count} 个响应块，总长度: {total_length} 字符")
                yield chunk

        logger.info(f"分析完成，共接收 {chunk_count} 个响应块，总长度: {total_length} 字符")
        logger.info(f"分析结果已保存到: {output_file}")

    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prompts")
async def get_prompts() -> Dict:
    """获取可用的提示词模板列表"""
    try:
        prompts = list_prompts()
        return {"success": True, "data": prompts}
    except Exception as e:
        logger.error(f"获取提示词模板失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyze")
async def analyze_paper(url: str, prompt_name: str = "yuanbao"):
    """分析论文API入口

    Args:
        url: 论文URL
        prompt_name: 提示词模板名称

    Returns:
        StreamingResponse: 流式响应对象
    """
    try:
        return StreamingResponse(
            process_paper_stream(url, prompt_name),
            media_type="text/plain"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理论文失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)