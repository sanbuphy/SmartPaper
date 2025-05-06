"""
与论文对话模块

提供一个简化的处理流程，从PDF论文下载、转换到与论文内容进行智能对话
"""

import os
import logging
import tempfile
import shutil
from typing import Optional, Union, Iterator, Callable, Tuple, Dict, Any

from SmartPaper.core.pdf_to_md import convert_pdf_to_markdown, PDFConverter
from SmartPaper.core.model_manager import ModelManager
from SmartPaper.get_arxiv.arxiv_downloader import download_paper
from SmartPaper.core.prompt_config import PromptConfig
from SmartPaper.core.pdf_cache import PDFCache

# 配置日志
logger = logging.getLogger(__name__)

# 默认系统提示词
DEFAULT_SYSTEM_PROMPT = "你是一个学术助手，专门帮助理解和分析论文。"


def download_and_chat_with_paper(
    paper_id: str,
    task_type: str = "coolpapaers",
    provider: Optional[str] = None,
    model: Optional[str] = None,
    config_path: Optional[str] = None,
    image_text_mode: bool = False,
    stream: bool = False,
    force_download: bool = False,
    use_cache: bool = True,
    pdf_cache_dir: Optional[str] = None,
    images_cache_dir: Optional[str] = None,
    **kwargs
) -> Union[str, Iterator[str]]:
    """
    下载arXiv论文并与之对话
    
    Args:
        paper_id: arXiv论文ID
        task_type: 任务类型，用于选择提示词模板
        provider: LLM提供商
        model: 模型名称
        config_path: 配置文件路径
        image_text_mode: 是否启用图文模式
        stream: 是否流式输出
        force_download: 是否强制重新下载
        use_cache: 是否使用缓存
        pdf_cache_dir: PDF缓存目录
        images_cache_dir: 图片缓存目录
        
    Returns:
        模型回复或流式回复迭代器
    """
    temp_dir = None
    paper_cache = None
    
    try:
        # 处理论文ID，去除空白字符
        paper_id = paper_id.strip()
        
        # 1. 创建临时目录和缓存
        temp_dir = tempfile.mkdtemp(prefix="smartpaper_")
        converter_type = 'fitz_with_image' if image_text_mode else 'fitz'
        
        # 2. 尝试从缓存获取论文内容或下载并处理
        pdf_path = None
        metadata = None
        md_content = ""
        
        if use_cache:
            # 使用论文ID作为缓存的key
            paper_cache = PDFCache(pdf_cache_dir=pdf_cache_dir, namespace=converter_type)
            
            if not force_download:
                # 尝试从缓存获取论文内容
                cached = paper_cache.get_by_paper_id(paper_id)
                if cached:
                    if 'pdf_path' in cached and os.path.exists(cached['pdf_path']):
                        pdf_path = cached['pdf_path']
                    if 'metadata' in cached:
                        metadata = cached['metadata']
                    if 'content' in cached:
                        md_content = cached['content']
                        logger.info(f"使用缓存论文内容: {paper_id}")
        
        # 如果没有找到缓存的PDF路径，下载论文
        if not pdf_path:
            logger.info(f"下载论文: {paper_id}")
            pdf_path, metadata = download_paper(paper_id, temp_dir, get_metadata=True)
        
        # 如果没有找到缓存的内容，转换PDF到Markdown
        if not md_content:
            logger.info(f"转换PDF为Markdown，模式: {converter_type}")
            md_content = convert_pdf_to_markdown(
                pdf_path=pdf_path,
                output_dir=temp_dir,
                converter_type=converter_type,
                strip_references=True,
                cache_dir=images_cache_dir
            )
            
            # 缓存处理结果
            if use_cache and paper_cache:
                metadata_dict = None
                if metadata:
                    metadata_dict = {
                        'title': metadata.title,
                        'authors': metadata.authors,
                        'categories': metadata.categories,
                        'published': metadata.published.isoformat() if metadata.published else None,
                        'abstract': metadata.abstract,
                        'web_url': metadata.web_url
                    }
                paper_cache.set_by_paper_id(paper_id, {
                    'pdf_path': pdf_path, 
                    'metadata': metadata_dict,
                    'content': md_content
                })
                logger.info(f"缓存论文内容: {paper_id}")
        
        # 4. 准备论文内容（添加元数据）
        content = prepare_paper_content(md_content, metadata)

        # 5. 初始化模型管理器和提示词配置
        model_manager = ModelManager(config_path=config_path)
        prompt_config = PromptConfig()
        
        # 6. 获取适当的模板
        prompt_type = 'llm_with_image' if image_text_mode else 'llm'
        template = prompt_config.get_prompt_template(prompt_type, task_type)
        
        # 7. 构建用户消息
        if not template:
            user_message = f"请分析以下论文内容：\n\n{content}"
        else:
            user_message = template.format(text=content)
        
        # 8. 调用模型获取回复 - 使用model_manager实例而不是导入的chat函数
        if stream:
            return model_manager.chat(
                message=user_message,
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                provider=provider,
                model=model,
                stream=True
            )
        else:
            return model_manager.chat(
                message=user_message, 
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                provider=provider,
                model=model,
                stream=False
            )
    
    finally:
        # 清理资源
        if paper_cache:
            paper_cache.close()
        
        if temp_dir and os.path.exists(temp_dir) and not kwargs.get("keep_temp", False):
            shutil.rmtree(temp_dir, ignore_errors=True)


def chat_with_local_paper(
    pdf_path: str,
    task_type: str = "coolpapaers",
    provider: Optional[str] = None,
    model: Optional[str] = None,
    config_path: Optional[str] = None,
    image_text_mode: bool = False,
    stream: bool = False,
    use_cache: bool = True,
    pdf_cache_dir: Optional[str] = None,
    images_cache_dir: Optional[str] = None,
    **kwargs
) -> Union[str, Iterator[str]]:
    """
    使用本地PDF论文进行对话
    
    Args:
        pdf_path: 本地PDF文件路径
        task_type: 任务类型，用于选择提示词模板
        provider: LLM提供商
        model: 模型名称
        config_path: 配置文件路径
        image_text_mode: 是否启用图文模式
        stream: 是否流式输出
        use_cache: 是否使用缓存
        pdf_cache_dir: PDF缓存目录
        images_cache_dir: 图片缓存目录
        
    Returns:
        模型回复或流式回复迭代器
    """
    temp_dir = None
    
    try:
        # 1. 验证文件存在
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"找不到PDF文件: {pdf_path}")
        
        # 2. 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix="smartpaper_local_")
        
        # 3. 转换PDF到Markdown
        converter_type = 'fitz_with_image' if image_text_mode else 'fitz'
        logger.info(f"转换本地PDF为Markdown，模式: {converter_type}")
        
        # 使用文件名作为缓存ID
        cache_id = os.path.basename(pdf_path).strip()
        
        if use_cache:
            pdf_cache = PDFCache(pdf_cache_dir=pdf_cache_dir, namespace="local_papers")
            cached_content = pdf_cache.get_by_paper_id(cache_id)
            if cached_content and 'content' in cached_content:
                md_content = cached_content['content']
                logger.info("使用缓存的PDF转换结果")
            else:
                md_content = convert_pdf_to_markdown(
                    pdf_path=pdf_path,
                    output_dir=temp_dir,
                    converter_type=converter_type,
                    strip_references=True,
                    cache_dir=images_cache_dir
                )
                pdf_cache.set_by_paper_id(cache_id, {'content': md_content})
            pdf_cache.close()
        else:
            md_content = convert_pdf_to_markdown(
                pdf_path=pdf_path,
                output_dir=temp_dir,
                converter_type=converter_type,
                strip_references=True,
                cache_dir=images_cache_dir
            )
        
        # 4. 准备论文内容（无元数据）
        content = f"## 论文正文\n\n{md_content}"
        
        # 5. 初始化模型管理器和提示词配置
        model_manager = ModelManager(config_path=config_path)
        prompt_config = PromptConfig()
        
        # 6. 获取适当的模板
        prompt_type = 'llm_with_image' if image_text_mode else 'llm'
        template = prompt_config.get_prompt_template(prompt_type, task_type)
        
        # 7. 构建用户消息
        if not template:
            user_message = f"请分析以下论文内容：\n\n{content}"
        else:
            user_message = template.format(text=content)
        
        # 8. 调用模型获取回复 - 使用model_manager实例而不是导入的chat函数
        if stream:
            return model_manager.chat(
                message=user_message,
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                provider=provider,
                model=model,
                stream=True
            )
        else:
            return model_manager.chat(
                message=user_message, 
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                provider=provider,
                model=model,
                stream=False
            )
    
    finally:
        # 清理资源
        if temp_dir and os.path.exists(temp_dir) and not kwargs.get("keep_temp", False):
            shutil.rmtree(temp_dir, ignore_errors=True)


def prepare_paper_content(markdown_content: str, metadata: Optional[Any]) -> str:
    """
    准备论文内容，包括元数据和正文
    
    Args:
        markdown_content: Markdown格式的论文内容
        metadata: 论文元数据，可以是ArxivPaper对象或元数据字典
    """
    # 如果没有元数据，直接返回内容
    if not metadata:
        return f"## 论文正文\n\n{markdown_content}"
    
    # 构建元数据部分
    metadata_section = "## 论文元数据\n\n"
    
    # 处理不同类型的元数据（兼容ArxivPaper对象和字典）
    if hasattr(metadata, 'categories') and hasattr(metadata, 'published'):
        # ArxivPaper对象
        # 添加分类和日期
        if metadata.categories:
            metadata_section += f"**分类:** {', '.join(metadata.categories)}\n\n"
        
        if metadata.published:
            metadata_section += f"**发布日期:** {metadata.published.strftime('%Y-%m-%d') if hasattr(metadata.published, 'strftime') else metadata.published}\n\n"
        
        # 添加摘要
        if metadata.abstract:
            metadata_section += f"**摘要:** {metadata.abstract}\n\n"
    else:
        # 字典类型元数据
        if metadata.get('categories'):
            metadata_section += f"**分类:** {', '.join(metadata['categories'])}\n\n"
        
        if metadata.get('published'):
            metadata_section += f"**发布日期:** {metadata['published']}\n\n"
        
        # 添加摘要
        if metadata.get('abstract'):
            metadata_section += f"**摘要:** {metadata['abstract']}\n\n"
    
    metadata_section += "---\n\n"
    
    # 合并元数据和论文内容
    return metadata_section + "## 论文正文\n\n" + markdown_content
