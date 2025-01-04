"""
API数据模型定义

定义了API请求和响应的数据结构
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatWithArxivPaperRequest(BaseModel):
    """从arXiv下载论文并对话的请求模型"""
    paper_id: str = Field(..., description="arXiv论文ID，如'2307.09288'")
    task_type: str = Field(default="coolpapaers", description="任务类型，影响提示词模板")
    provider: Optional[str] = Field(default=None, description="LLM提供商")
    model: Optional[str] = Field(default=None, description="模型名称") 
    image_text_mode: bool = Field(default=False, description="是否启用图文模式")
    use_cache: bool = Field(default=True, description="是否使用缓存")
    stream: bool = Field(default=False, description="是否使用流式输出")
    force_download: bool = Field(default=False, description="是否强制重新下载论文，不使用缓存")


class ChatWithLocalPaperRequest(BaseModel):
    """与本地论文对话的请求模型"""
    pdf_path: str = Field(..., description="本地PDF文件路径")
    task_type: str = Field(default="coolpapaers", description="任务类型，影响提示词模板")
    provider: Optional[str] = Field(default=None, description="LLM提供商")
    model: Optional[str] = Field(default=None, description="模型名称")
    image_text_mode: bool = Field(default=False, description="是否启用图文模式")
    use_cache: bool = Field(default=True, description="是否使用缓存")
    stream: bool = Field(default=False, description="是否使用流式输出")


class UploadPaperRequest(BaseModel):
    """上传PDF论文的请求模型"""
    file_name: str = Field(..., description="文件名称")
    content_type: str = Field(default="application/pdf", description="文件内容类型")


class PaperMetadata(BaseModel):
    """论文元数据"""
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    published: Optional[str] = None
    abstract: Optional[str] = None
    comment: Optional[str] = None
    journal_ref: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="LLM生成的响应")
    paper_metadata: Optional[PaperMetadata] = Field(default=None, description="论文元数据")
    success: bool = Field(..., description="请求是否成功")
    error: Optional[str] = Field(default=None, description="错误信息")


class StreamResponse(BaseModel):
    """流式响应的单个消息"""
    content: str = Field(..., description="消息内容")
    done: bool = Field(..., description="是否是最后一条消息")


class UploadResponse(BaseModel):
    """文件上传响应"""
    file_id: str = Field(..., description="上传文件的ID")
    file_path: str = Field(..., description="服务器上的文件路径")
    success: bool = Field(..., description="上传是否成功")
    error: Optional[str] = Field(default=None, description="错误信息")


class ModelInfo(BaseModel):
    """模型信息"""
    name: str = Field(..., description="模型名称")
    context_length: int = Field(default=32768, description="模型上下文长度")


class ProviderInfo(BaseModel):
    """提供商信息"""
    name: str = Field(..., description="提供商名称")
    models: List[ModelInfo] = Field(default_list=[], description="可用模型列表")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=4096, description="最大生成token数")


class ConfigResponse(BaseModel):
    """配置响应"""
    providers: List[ProviderInfo] = Field(default_list=[], description="所有可用提供商信息")
    default_provider: str = Field(..., description="默认提供商")
    default_model: Optional[str] = Field(default=None, description="默认模型")
    success: bool = Field(..., description="请求是否成功")
    error: Optional[str] = Field(default=None, description="错误信息")


class UpdateConfigRequest(BaseModel):
    """更新配置请求"""
    provider: Optional[str] = Field(default=None, description="更新默认提供商")
    default_model_index: Optional[int] = Field(default=None, description="更新默认模型索引")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    temperature: Optional[float] = Field(default=None, description="温度参数")
    max_tokens: Optional[int] = Field(default=None, description="最大生成token数")
    target_provider: Optional[str] = Field(default=None, description="目标提供商(如果不是默认提供商)")


class ReloadConfigResponse(BaseModel):
    """重载配置响应"""
    success: bool = Field(..., description="重载是否成功")
    error: Optional[str] = Field(default=None, description="错误信息")


class PromptTemplate(BaseModel):
    """提示词模板"""
    template: str = Field(..., description="提示词模板内容")
    description: Optional[str] = Field(default=None, description="提示词描述")


class PromptListResponse(BaseModel):
    """提示词列表响应"""
    prompts: Dict[str, List[str]] = Field(..., description="按类型组织的提示词列表")
    success: bool = Field(..., description="请求是否成功")
    error: Optional[str] = Field(default=None, description="错误信息")


class PromptDetailResponse(BaseModel):
    """提示词详情响应"""
    template: Optional[str] = Field(default=None, description="提示词模板内容")
    description: Optional[str] = Field(default=None, description="提示词描述")
    success: bool = Field(..., description="请求是否成功")
    error: Optional[str] = Field(default=None, description="错误信息")


class PromptUpdateRequest(BaseModel):
    """更新提示词请求"""
    prompt_type: str = Field(..., description="提示词类型，如llm或llm_with_image")
    prompt_name: str = Field(..., description="提示词名称")
    template: str = Field(..., description="提示词模板内容")
    description: Optional[str] = Field(default=None, description="提示词描述")


class PromptUpdateResponse(BaseModel):
    """更新提示词响应"""
    success: bool = Field(..., description="更新是否成功")
    error: Optional[str] = Field(default=None, description="错误信息")


class PromptDeleteRequest(BaseModel):
    """删除提示词请求"""
    prompt_type: str = Field(..., description="提示词类型，如llm或llm_with_image")
    prompt_name: str = Field(..., description="提示词名称")
