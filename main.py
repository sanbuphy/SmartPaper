"""
SmartPaper API服务主入口

启动FastAPI服务，提供论文对话的API接口
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api import router as api_router
from app.utils.utils import ensure_directory, get_upload_path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="SmartPaper API",
    description="智能论文对话系统API接口",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)

# 确保上传目录存在
upload_dir = get_upload_path()
ensure_directory(upload_dir)

# 挂载静态文件目录（如果有前端页面）
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("全局异常")
    return JSONResponse(
        status_code=500,
        content={"message": "发生内部服务器错误", "detail": str(exc)}
    )

# 添加健康检查端点
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

# 根路径重定向
@app.get("/")
async def root():
    # 返回html页面，可以跳转docs
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartPaper API</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        h1 { color: #333; }
        a { text-decoration: none; color: #007BFF; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>欢迎使用 SmartPaper API</h1>
    <p>API文档请访问：<a href="/docs">Swagger UI</a></p>
    <p>API文档请访问：<a href="/redoc">ReDoc</a></p>
    <p>健康检查请访问：<a href="/health">/health</a></p>

"""


if __name__ == "__main__":
    # 运行服务器
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 900)),
        reload=True
    )
