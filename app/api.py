"""
API端点定义

实现SmartPaper的API接口
"""

import os
from typing import Optional
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse

from SmartPaper.core.chat_with_paper import (
    download_and_chat_with_paper,
    chat_with_local_paper,
)

# 导入应用配置 - 添加获取配置路径的函数
from app.config import get_pdf_cache_dir, get_images_cache_dir, get_uploads_dir, get_config_path

from app.models import (
    ChatWithArxivPaperRequest,
    ChatWithLocalPaperRequest,
    ChatResponse,
    UploadResponse,
    ConfigResponse,
    UpdateConfigRequest,
    ReloadConfigResponse,
    PromptListResponse,
    PromptDetailResponse,
    PromptUpdateRequest, 
    PromptUpdateResponse,
    PromptDeleteRequest
)

from app.utils.utils import (
    save_uploaded_file, 
    SSEStreamer, 
    get_providers_info,
    update_config,
    reload_config,
    get_prompt_list,
    get_prompt_detail,
    update_prompt,
    delete_prompt,
    reload_prompts
)

# 配置日志
logger = logging.getLogger(__name__)



# 创建路由器
router = APIRouter(tags=["paper_chat"])

# 临时存储流式回调结果的字典
stream_results = {}


@router.post("/chat_with_arxiv", response_model=ChatResponse)
async def chat_with_arxiv(request: ChatWithArxivPaperRequest):
    """
    从arXiv下载论文并与之对话
    """
    try:
        if request.stream:
            raise HTTPException(
                status_code=400,
                detail="此端点不支持流式输出，请使用 /chat_with_arxiv_stream"
            )
            
        # 调用简化后的函数
        response = download_and_chat_with_paper(
            paper_id=request.paper_id,
            task_type=request.task_type,
            provider=request.provider,
            model=request.model,
            image_text_mode=request.image_text_mode,
            use_cache=request.use_cache,
            stream=False,
            force_download=request.force_download,
            pdf_cache_dir=get_pdf_cache_dir(),
            images_cache_dir=get_images_cache_dir(),
            config_path=get_config_path()
        )
        
        return ChatResponse(
            response=response,
            success=True,
            paper_metadata=None
        )
    except Exception as e:
        logger.exception("与arXiv论文对话时出错")
        return ChatResponse(
            response="",
            success=False,
            error=str(e)
        )


@router.post("/chat_with_arxiv_stream")
async def chat_with_arxiv_stream(request: ChatWithArxivPaperRequest):
    """
    从arXiv下载论文并进行流式对话
    """
    try:
        # 使用简化后的函数获取流式响应
        response_iterator = download_and_chat_with_paper(
            paper_id=request.paper_id,
            task_type=request.task_type,
            provider=request.provider,
            model=request.model,
            image_text_mode=request.image_text_mode,
            use_cache=request.use_cache,
            stream=True,
            force_download=request.force_download,
            pdf_cache_dir=get_pdf_cache_dir(),
            images_cache_dir=get_images_cache_dir(),
            config_path=get_config_path(),
            keep_temp=False  # 确保处理完后清理临时文件
        )
        
        # 创建SSE流响应，使用带图片处理的流式生成器
        return StreamingResponse(
            SSEStreamer.stream_generator_with_image_processing(
                response_iterator,
                get_images_cache_dir()
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.exception("与arXiv论文流式对话时出错")
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500
        )


@router.post("/chat_with_local", response_model=ChatResponse)
async def chat_with_local(request: ChatWithLocalPaperRequest):
    """
    与本地论文文件对话
    """
    try:
        if request.stream:
            raise HTTPException(
                status_code=400,
                detail="此端点不支持流式输出，请使用 /chat_with_local_stream"
            )
            
        # 检查文件是否存在
        if not os.path.exists(request.pdf_path):
            raise HTTPException(
                status_code=404,
                detail=f"找不到文件: {request.pdf_path}"
            )
            
        # 使用简化后的函数
        response = chat_with_local_paper(
            pdf_path=request.pdf_path,
            task_type=request.task_type,
            provider=request.provider,
            model=request.model,
            image_text_mode=request.image_text_mode,
            use_cache=request.use_cache,
            stream=False,
            pdf_cache_dir=get_pdf_cache_dir(),
            images_cache_dir=get_images_cache_dir(),
            config_path=get_config_path(),
            keep_temp=False  # 确保处理完后清理临时文件
        )
        
        return ChatResponse(
            response=response,
            success=True
        )
    except Exception as e:
        logger.exception("与本地论文对话时出错")
        return ChatResponse(
            response="",
            success=False,
            error=str(e)
        )


@router.post("/chat_with_local_stream")
async def chat_with_local_stream(request: ChatWithLocalPaperRequest):
    """
    与本地论文进行流式对话
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(request.pdf_path):
            raise HTTPException(
                status_code=404,
                detail=f"找不到文件: {request.pdf_path}"
            )
            
        # 使用简化后的函数获取流式响应
        response_iterator = chat_with_local_paper(
            pdf_path=request.pdf_path,
            task_type=request.task_type,
            provider=request.provider,
            model=request.model,
            image_text_mode=request.image_text_mode,
            use_cache=request.use_cache,
            stream=True,
            pdf_cache_dir=get_pdf_cache_dir(),
            images_cache_dir=get_images_cache_dir(),
            config_path=get_config_path(),
            keep_temp=False  # 确保处理完后清理临时文件
        )
        
        # 创建SSE流响应，使用带图片处理的流式生成器
        return StreamingResponse(
            SSEStreamer.stream_generator_with_image_processing(
                response_iterator,
                get_images_cache_dir()
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.exception("与本地论文流式对话时出错")
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500
        )


@router.post("/upload_paper", response_model=UploadResponse)
async def upload_paper(file: UploadFile = File(...)):
    """
    上传PDF论文文件
    """
    try:
        # 检查文件类型
        if not file.content_type or "pdf" not in file.content_type.lower():
            raise HTTPException(
                status_code=400,
                detail="只接受PDF文件"
            )
            
        # 读取文件内容
        file_content = await file.read()
        
        # 保存文件
        result = save_uploaded_file(file_content, file.filename)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"保存文件失败: {result.get('error', '未知错误')}"
            )
            
        return UploadResponse(
            file_id=result["file_id"],
            file_path=result["file_path"],
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("上传文件时出错")
        return UploadResponse(
            file_id="",
            file_path="",
            success=False,
            error=str(e)
        )


@router.get("/list_uploaded_papers")
async def list_uploaded_papers():
    """
    列出已上传的论文文件
    """
    try:
        # 使用配置中的上传路径
        upload_dir = get_uploads_dir()
        files = []
        
        for filename in os.listdir(upload_dir):
            if filename.endswith(".pdf"):
                file_path = os.path.join(upload_dir, filename)
                file_id = filename.split("_")[0] if "_" in filename else "unknown"
                
                files.append({
                    "file_id": file_id,
                    "file_name": filename,
                    "file_path": file_path,
                    "size_bytes": os.path.getsize(file_path)
                })
                
        return {"success": True, "files": files}
    except Exception as e:
        logger.exception("列出上传文件时出错")
        return {"success": False, "error": str(e), "files": []}


@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """
    获取配置信息，包括可用的模型和提供商
    """
    try:
        result = get_providers_info()
        return ConfigResponse(
            providers=result["providers"],
            default_provider=result["default_provider"],
            default_model=result["default_model"],
            success=result["success"],
            error=result.get("error")
        )
    except Exception as e:
        logger.exception("获取配置信息时出错")
        return ConfigResponse(
            providers=[],
            default_provider="",
            default_model=None,
            success=False,
            error=str(e)
        )


@router.post("/config", response_model=ConfigResponse)
async def update_app_config(request: UpdateConfigRequest):
    """
    更新配置信息
    """
    try:
        # 将请求转为字典格式
        update_data = request.dict(exclude_none=True)
        
        # 更新配置
        result = update_config(update_data)
        
        if not result["success"]:
            return ConfigResponse(
                providers=[],
                default_provider="",
                default_model=None,
                success=False,
                error=result.get("error", "更新配置失败")
            )
            
        # 获取更新后的配置信息
        updated_config = get_providers_info()
        
        return ConfigResponse(
            providers=updated_config["providers"],
            default_provider=updated_config["default_provider"],
            default_model=updated_config["default_model"],
            success=True
        )
    except Exception as e:
        logger.exception("更新配置信息时出错")
        return ConfigResponse(
            providers=[],
            default_provider="",
            default_model=None,
            success=False,
            error=str(e)
        )


@router.post("/config/reload", response_model=ReloadConfigResponse)
async def reload_app_config():
    """
    重新加载配置文件
    """
    try:
        result = reload_config()
        return ReloadConfigResponse(
            success=result["success"],
            error=result.get("error")
        )
    except Exception as e:
        logger.exception("重新加载配置时出错")
        return ReloadConfigResponse(
            success=False,
            error=str(e)
        )


@router.get("/models")
async def list_models():
    """
    获取所有可用模型列表，通过Config类获取
    """
    try:
        # 使用Config类直接获取配置
        from SmartPaper.core.config import Config
        config = Config(get_config_path())
        
        # 获取所有提供商
        providers = []
        for provider_key in config.get('llm', {}).keys():
            # 排除非提供商配置键
            if provider_key in ['provider', 'max_requests', 'default_model_index']:
                continue
                
            provider_config = config.get(f'llm.{provider_key}', {})
            models_config = provider_config.get('models', [])
            
            # 处理不同格式的模型配置
            models = []
            if models_config:
                if isinstance(models_config[0], dict):
                    # 新格式 - 包含名称和上下文长度的字典
                    models = models_config
                else:
                    # 旧格式 - 仅包含名称的字符串列表
                    models = [{"name": model, "context_length": 32768} for model in models_config]
            
            providers.append({
                "name": provider_key,
                "models": models
            })
        
        # 获取默认提供商和模型
        default_provider = config.llm_provider
        default_model = config.default_model
        
        all_models = []
        for provider in providers:
            provider_name = provider["name"]
            for model in provider["models"]:
                all_models.append({
                    "provider": provider_name,
                    "name": model["name"],
                    "context_length": model.get("context_length", 32768)
                })
                
        return {
            "models": all_models,
            "default_provider": default_provider,
            "default_model": default_model,
            "success": True
        }
    except Exception as e:
        logger.exception("获取模型列表时出错")
        return {
            "models": [],
            "default_provider": "",
            "default_model": None,
            "success": False,
            "error": str(e)
        }


# 创建提示词相关的路由
prompt_router = APIRouter(prefix="/prompts", tags=["prompts"])

@prompt_router.get("/list", response_model=PromptListResponse)
async def list_prompts(prompt_type: Optional[str] = None):
    """
    获取提示词列表
    
    Args:
        prompt_type: 可选的提示词类型过滤器，如llm或llm_with_image
    """
    try:
        result = get_prompt_list(prompt_type)
        return PromptListResponse(
            prompts=result["prompts"],
            success=result["success"],
            error=result.get("error")
        )
    except Exception as e:
        logger.exception("获取提示词列表时出错")
        return PromptListResponse(
            prompts={},
            success=False,
            error=str(e)
        )

@prompt_router.get("/detail/{prompt_type}/{prompt_name}", response_model=PromptDetailResponse)
async def get_prompt(prompt_type: str, prompt_name: str):
    """
    获取提示词详情
    
    Args:
        prompt_type: 提示词类型，如llm或llm_with_image
        prompt_name: 提示词名称
    """
    try:
        result = get_prompt_detail(prompt_type, prompt_name)
        return PromptDetailResponse(
            template=result.get("template"),
            description=result.get("description"),
            success=result["success"],
            error=result.get("error")
        )
    except Exception as e:
        logger.exception("获取提示词详情时出错")
        return PromptDetailResponse(
            template=None,
            description=None,
            success=False,
            error=str(e)
        )

@prompt_router.post("/update", response_model=PromptUpdateResponse)
async def update_prompt_endpoint(request: PromptUpdateRequest):
    """
    更新或创建提示词
    """
    try:
        result = update_prompt(
            prompt_type=request.prompt_type,
            prompt_name=request.prompt_name,
            template=request.template,
            description=request.description
        )
        
        return PromptUpdateResponse(
            success=result["success"],
            error=result.get("error")
        )
    except Exception as e:
        logger.exception("更新提示词时出错")
        return PromptUpdateResponse(
            success=False,
            error=str(e)
        )

@prompt_router.post("/delete", response_model=PromptUpdateResponse)
async def delete_prompt_endpoint(request: PromptDeleteRequest):
    """
    删除提示词
    """
    try:
        result = delete_prompt(
            prompt_type=request.prompt_type,
            prompt_name=request.prompt_name
        )
        
        return PromptUpdateResponse(
            success=result["success"],
            error=result.get("error")
        )
    except Exception as e:
        logger.exception("删除提示词时出错")
        return PromptUpdateResponse(
            success=False,
            error=str(e)
        )

@prompt_router.post("/reload", response_model=ReloadConfigResponse)
async def reload_prompts_endpoint():
    """
    重新加载所有提示词
    """
    try:
        result = reload_prompts()
        return ReloadConfigResponse(
            success=result["success"],
            error=result.get("error")
        )
    except Exception as e:
        logger.exception("重新加载提示词时出错")
        return ReloadConfigResponse(
            success=False,
            error=str(e)
        )

@prompt_router.get("/task_types")
async def list_task_types():
    """
    获取所有可用的任务类型
    """
    try:
        # 获取所有提示词
        result = get_prompt_list()
        
        if not result["success"]:
            return {
                "task_types": [],
                "success": False,
                "error": result.get("error", "获取提示词列表失败")
            }
            
        # 提取任务类型（即提示词名称）
        prompts = result["prompts"]
        task_types = set()
        
        # 从llm和llm_with_image类型中提取任务类型
        for prompt_type in prompts:
            for task_type in prompts[prompt_type]:
                task_types.add(task_type)
        
        return {
            "task_types": sorted(list(task_types)),
            "success": True
        }
    except Exception as e:
        logger.exception("获取任务类型列表时出错")
        return {
            "task_types": [],
            "success": False,
            "error": str(e)
        }

@prompt_router.get("/task_descriptions")
async def get_task_descriptions():
    """
    获取任务类型的描述信息，通过PromptConfig类直接获取
    """
    try:
        # 使用PromptConfig类
        from SmartPaper.core.prompt_config import PromptConfig
        prompt_config = PromptConfig()
        
        # 获取所有提示词
        prompts = prompt_config.list_prompts()
        descriptions = {}
        
        # 从所有提示词中提取描述
        for prompt_type, tasks in prompts.items():
            for task_name, task_info in tasks.items():
                if task_name not in descriptions:
                    # 如果是字符串，则创建一个默认描述
                    if isinstance(task_info, str):
                        descriptions[task_name] = f"{task_name} 任务"
                    # 如果是字典且包含描述，则使用该描述
                    elif isinstance(task_info, dict) and 'description' in task_info:
                        descriptions[task_name] = task_info['description']
                    else:
                        descriptions[task_name] = f"{task_name} 任务"
        
        return {
            "descriptions": descriptions,
            "success": True
        }
    except Exception as e:
        logger.exception("获取任务描述时出错")
        return {
            "descriptions": {},
            "success": False,
            "error": str(e)
        }

# 注册提示词路由
router.include_router(prompt_router, prefix="/api/v1")
