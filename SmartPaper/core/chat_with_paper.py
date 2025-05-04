"""
与论文对话模块

提供一个完整的处理流程，从PDF论文下载、转换到与论文内容进行智能对话
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Iterator, Callable, Any, Tuple
import logging
import tempfile
import shutil

from SmartPaper.core.pdf_to_md import convert_pdf_to_markdown, PDFConverter
from SmartPaper.core.model_manager import ModelManager, chat, chat_with_history, stream_callback as llm_stream_callback
from SmartPaper.get_arxiv.arxiv_downloader import download_paper
from SmartPaper.get_arxiv.arxiv_client import ArxivPaper
from SmartPaper.core.prompt_config import PromptConfig
from SmartPaper.core.pdf_cache import PDFCache
from SmartPaper.core.config import Config  # 添加导入 Config 类

# 配置日志
logger = logging.getLogger(__name__)

# 默认角色提示词 - 简化为基本角色定义
DEFAULT_SYSTEM_PROMPT = "你是一个学术助手，专门帮助理解和分析论文。"

class PDFProcessor:
    """
    PDF处理器类
    
    负责处理PDF转换为Markdown的逻辑，可配置不同的转换器类型
    """
    
    def __init__(
        self, 
        converter_type: str = 'fitz',
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
        cache_namespace: str = 'pdf_processor'
    ):
        """
        初始化PDF处理器
        
        Args:
            converter_type: 转换器类型，如'fitz'或'fitz_with_image'
            cache_dir: PDF解析结果缓存目录，用于存储解析后的PDF内容，不是存储图片的缓存目录
            use_cache: 是否使用缓存
            cache_namespace: 缓存命名空间
        """
        self.converter_type = converter_type
        self.converter = PDFConverter(converter_type=converter_type)
        
        # 初始化缓存 - 始终启用缓存
        self.use_cache = True  # 强制启用缓存
        self.pdf_cache = PDFCache(cache_dir, namespace=cache_namespace)
            
        # 当前处理的PDF路径和内容
        self.current_pdf_path = None
        self.current_content = None
    
    def process_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        strip_references: bool = True,
        images_cache_dir: Optional[str] = None,  # 专门用于存储图片的缓存目录
        delete_rendered_images: bool = True,
        cache_base64: bool = True,
        api_key: Optional[str] = None
    ) -> str:
        """
        处理PDF文件并转换为Markdown
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，用于存储临时处理文件
            strip_references: 是否去除参考文献
            images_cache_dir: 图片缓存目录，仅在使用带图像的转换器时有效，用于存储提取的图片
            delete_rendered_images: 是否删除渲染的图像(仅图像模式有效)
            cache_base64: 是否缓存base64编码的图像(仅图像模式有效)
            api_key: 图像API密钥(仅图像模式有效)
        
        Returns:
            转换后的Markdown文本
        """
        if not pdf_path or not os.path.exists(pdf_path):
            raise FileNotFoundError(f"找不到PDF文件: {pdf_path}")
        
        self.current_pdf_path = pdf_path
        
        # 准备处理参数，用于缓存键
        process_params = {
            'strip_references': strip_references,
            'delete_rendered_images': delete_rendered_images,
            'cache_base64': cache_base64
        }
        
        # 尝试从缓存获取结果 - 始终检查缓存
        cached_result = self.pdf_cache.get(
            pdf_path=pdf_path,
            converter_type=self.converter_type,
            params=process_params
        )
        
        if cached_result:
            logger.info(f"使用缓存的PDF转换结果")
            self.current_content = cached_result
            return cached_result
        
        # 确保输出目录存在
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="smartpaper_md_")
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # 转换PDF到Markdown
        logger.info(f"正在将论文转换为Markdown，使用转换器: {self.converter_type}")
        
        # 直接调用转换函数，传入明确的参数
        if self.converter_type == 'fitz_with_image':
            # 图文模式下的转换参数
            markdown_content = convert_pdf_to_markdown(
                pdf_path=pdf_path,
                output_dir=output_dir,
                converter_type=self.converter_type,
                strip_references=strip_references,
                cache_dir=images_cache_dir,  # 图片缓存目录
                delete_rendered_images=delete_rendered_images,
                cache_base64=cache_base64,
                api_key=api_key
            )
        else:
            # 纯文本模式下的转换参数
            markdown_content = convert_pdf_to_markdown(
                pdf_path=pdf_path,
                output_dir=output_dir,
                converter_type=self.converter_type,
                strip_references=strip_references
            )
        
        # 存储结果到缓存
        self.pdf_cache.set(
            pdf_path=pdf_path,
            converter_type=self.converter_type,
            params=process_params,
            result=markdown_content
        )
        
        logger.info(f"论文已转换为Markdown，长度: {len(markdown_content)} 字符")
        self.current_content = markdown_content
        
        return markdown_content
    
    def close(self):
        """关闭和清理资源"""
        if self.use_cache and self.pdf_cache:
            self.pdf_cache.close()
        
        self.current_pdf_path = None
        self.current_content = None
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class PaperChat:
    """
    论文对话类
    
    通过组合PDF处理器和LLM模型，实现与论文对话的功能
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        prompt_config_path: Optional[str] = None,
        model_manager: Optional[ModelManager] = None,
        pdf_processor: Optional[PDFProcessor] = None,
        image_text_mode: bool = False,
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
        prompt_type: str = 'llm'
    ):
        """
        初始化论文对话系统
        
        Args:
            config_path: 配置文件路径
            prompt_config_path: 提示词配置文件路径
            model_manager: 模型管理器实例
            pdf_processor: PDF处理器实例
            image_text_mode: 是否使用图文模式
            cache_dir: 缓存目录
            use_cache: 是否使用缓存
            prompt_type: 提示词类型
        """
        # 初始化模型管理器
        self.model_manager = model_manager if model_manager else ModelManager(config_path=config_path)
        
        # 加载提示词配置
        self.prompt_config = PromptConfig(prompt_config_path)
        self.prompt_type = prompt_type if prompt_type else ('llm_with_image' if image_text_mode else 'llm')
        
        # 初始化PDF处理器
        if (pdf_processor):
            self.pdf_processor = pdf_processor
        else:
            converter_type = 'fitz_with_image' if image_text_mode else 'fitz'
            cache_namespace = 'image_paper_chat' if image_text_mode else 'text_paper_chat'
            self.pdf_processor = PDFProcessor(
                converter_type=converter_type,
                cache_dir=cache_dir,
                use_cache=use_cache,
                cache_namespace=cache_namespace
            )
        
        # 初始化论文缓存
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        if use_cache:
            self.arxiv_cache = PDFCache(cache_dir=cache_dir, namespace="arxiv_papers")
        else:
            self.arxiv_cache = None
            
        # 当前论文元数据
        self.current_paper_metadata = None
        
        # 临时目录跟踪
        self.temp_dirs = []

    def download_paper_from_arxiv(
        self, 
        paper_id: str, 
        output_dir: Optional[str] = None,
        force_download: bool = False
    ) -> Tuple[str, Optional[ArxivPaper]]:
        """
        从arXiv下载论文，支持缓存
        
        Args:
            paper_id: arXiv论文ID
            output_dir: 输出目录
            force_download: 是否强制重新下载，忽略缓存
            
        Returns:
            (论文PDF路径, 论文元数据)
        """
        # 尝试从缓存获取论文信息
        cached_result = None
        if self.use_cache and self.arxiv_cache and not force_download:
            cached_result = self.arxiv_cache.get_by_paper_id(paper_id)
            
        if cached_result and os.path.exists(cached_result['pdf_path']):
            logger.info(f"使用缓存的arXiv论文: {paper_id}")
            pdf_path = cached_result['pdf_path']
            # 重建元数据对象
            metadata = ArxivPaper(**cached_result['metadata']) if cached_result.get('metadata') else None
            self.current_paper_metadata = metadata
            return pdf_path, metadata
            
        # 如果没有缓存或强制下载，则执行下载
        if output_dir is None:
            # 使用临时目录
            output_dir = tempfile.mkdtemp(prefix="smartpaper_")
            # 记录临时目录用于后续清理
            self.temp_dirs.append(output_dir)
        else:
            os.makedirs(output_dir, exist_ok=True)
            
        logger.info(f"正在从arXiv下载论文: {paper_id}")
        pdf_path, metadata = download_paper(
            paper_id=paper_id,
            output_dir=output_dir,
            get_metadata=True
        )
        
        logger.info(f"论文已下载到: {pdf_path}")
        self.current_paper_metadata = metadata
        
        # 缓存下载结果
        if self.use_cache and self.arxiv_cache:
            # 准备用于缓存的元数据
            metadata_dict = None
            if metadata:
                # 将ArxivPaper对象转换为可序列化的字典
                metadata_dict = {
                    'title': metadata.title,
                    'authors': metadata.authors,
                    'categories': metadata.categories,
                    'published': metadata.published.isoformat() if metadata.published else None,
                    'updated': metadata.updated.isoformat() if metadata.updated else None,
                    'abstract': metadata.abstract,
                    'comment': metadata.comment,
                    'journal_ref': metadata.journal_ref,
                    'doi': metadata.doi,
                    'arxiv_url': metadata.web_url
                }
                
            cache_data = {
                'pdf_path': pdf_path,
                'metadata': metadata_dict
            }
            self.arxiv_cache.set_by_paper_id(paper_id, cache_data)
        
        return pdf_path, metadata

    def load_paper_from_file(
        self, 
        pdf_path: str
    ) -> str:
        """
        从本地文件加载论文
        
        Args:
            pdf_path: 论文PDF文件路径
            
        Returns:
            论文文件路径
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"找不到PDF文件: {pdf_path}")
            
        logger.info(f"加载本地论文文件: {pdf_path}")
        self.current_paper_metadata = None
        
        return pdf_path
    
    def convert_paper_to_markdown(
        self, 
        pdf_path: str,
        output_dir: Optional[str] = None,
        strip_references: bool = True,
        images_cache_dir: Optional[str] = None,
        delete_rendered_images: bool = True,
        cache_base64: bool = True,
        api_key: Optional[str] = None
    ) -> str:
        """
        将论文PDF转换为Markdown
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            strip_references: 是否去除参考文献
            images_cache_dir: 图片缓存目录(图文模式)
            delete_rendered_images: 是否删除渲染的图像(图文模式)
            cache_base64: 是否缓存base64编码的图像(图文模式)
            api_key: 图像API密钥(图文模式)
            
        Returns:
            转换后的Markdown文本
        """
        return self.pdf_processor.process_pdf(
            pdf_path=pdf_path,
            output_dir=output_dir,
            strip_references=strip_references,
            images_cache_dir=images_cache_dir,
            delete_rendered_images=delete_rendered_images,
            cache_base64=cache_base64,
            api_key=api_key
        )
    
    def prepare_combined_content(self) -> str:
        """
        准备完整的论文内容，包括元数据和正文
        
        Returns:
            合并后的论文内容文本
        """
        if not self.pdf_processor.current_content:
            raise ValueError("请先加载论文并转换为Markdown")
            
        # 准备元数据信息
        metadata_section = ""
        if self.current_paper_metadata:
            metadata_section = "## 论文元数据\n\n"
            
            # 标题始终显示
            metadata_section += f"**分类:** {', '.join(self.current_paper_metadata.categories)}\n\n"
            metadata_section += f"**发布日期:** {self.current_paper_metadata.published.strftime('%Y-%m-%d')}\n\n"
            
            if self.current_paper_metadata.abstract:
                metadata_section += f"**摘要:** {self.current_paper_metadata.abstract}\n\n"
            
            if self.current_paper_metadata.comment:
                metadata_section += f"**评论:** {self.current_paper_metadata.comment}\n\n"
                
            if self.current_paper_metadata.journal_ref:
                metadata_section += f"**期刊引用:** {self.current_paper_metadata.journal_ref}\n\n"
            
            metadata_section += "---\n\n"
            
        # 合并元数据和论文内容
        combined_content = metadata_section + "## 论文正文\n\n" + self.pdf_processor.current_content
        
        return combined_content
        
    def truncate_content(self, content: str, max_length: int) -> str:
        """
        截断内容，确保不超过模型的上下文长度限制
        当上下文长度不够时，优先去除元数据，保留更多的正文内容
        
        Args:
            content: 要截断的内容
            max_length: 最大允许长度
            
        Returns:
            截断后的内容
        """
        if len(content) <= max_length:
            return content
        
        # 预留2000个字符的空间用于系统提示词、用户问题等
        safe_length = max_length - 2000
        
        logger.info(f"内容过长({len(content)}字符)，截断至{safe_length}字符")
        
        # 查找元数据部分和正文部分
        metadata_end = content.find("---\n\n")
        if (metadata_end != -1):
            metadata_part = content[:metadata_end + 5]  # 包括 "---\n\n"
            main_content_start = content.find("## 论文正文")
            if (main_content_start != -1):
                # 找到了论文正文的标记
                main_content = content[main_content_start:]
                
                # 如果正文部分已经超过安全长度，直接只保留正文部分（可能还需要截断）
                if (len(main_content) > safe_length):
                    logger.info("正文内容已超过安全长度，优先去除元数据")
                    result = main_content[:safe_length] + "\n\n...(内容已截断)..."
                else:
                    # 正文部分没超过安全长度，可以考虑保留部分元数据
                    remaining_length = safe_length - len(main_content)
                    if (remaining_length > 100):  # 如果剩余空间足够放一些有意义的元数据
                        # 优先保留标题和作者信息
                        title_end = metadata_part.find("**作者:**")
                        if (title_end != -1 and title_end < remaining_length):
                            # 可以放下标题
                            authors_end = metadata_part.find("\n\n", title_end)
                            if (authors_end != -1 and authors_end < remaining_length):
                                # 可以放下作者
                                partial_metadata = metadata_part[:authors_end + 2]
                            else:
                                partial_metadata = metadata_part[:title_end] + "...\n\n"
                        else:
                            partial_metadata = ""
                        
                        result = partial_metadata + main_content
                    else:
                        # 剩余空间太小，只保留正文
                        result = main_content
            else:
                # 找不到正文标记，退回到基本的截断逻辑
                main_content = content[metadata_end + 5:]
                
                # 计算正文可保留的长度
                remaining_length = safe_length - len(metadata_part)
                if (remaining_length <= 0):
                    # 如果元数据已经很长，只保留部分正文，去掉元数据
                    result = content[metadata_end + 5:metadata_end + 5 + safe_length] + "\n\n...(内容已截断)..."
                else:
                    # 截断正文部分
                    truncated_main = main_content[:remaining_length]
                    result = metadata_part + truncated_main + "\n\n...(内容已截断)..."
        else:
            # 没有找到元数据分隔符，直接截断
            result = content[:safe_length] + "\n\n...(内容已截断)..."
            
        return result
    
    def get_model_context_length(self, provider: Optional[str] = None, model: Optional[str] = None) -> int:
        """
        获取模型的最大上下文长度
        
        Args:
            provider: LLM提供商
            model: 模型名称
            
        Returns:
            模型最大上下文长度，默认为32768字符
        """
        # 默认上下文长度
        default_length = 32768
        
        # 如果没有指定provider或model，使用默认值
        if not provider or not model:
            return default_length
        
        try:
            # 尝试从模型管理器获取上下文长度
            context_length = self.model_manager.get_model_context_length(provider, model)
            return context_length if context_length else default_length
        except:
            # 如果发生错误，返回默认值
            return default_length
        
    def chat_with_paper(
        self,
        task_type: str = "coolpapaers",
        provider: Optional[str] = None, 
        model: Optional[str] = None,
        stream: bool = False,
        cleanup_after_chat: bool = True
    ) -> Union[str, Iterator[str]]:
        """
        与论文进行对话
        
        Args:
            task_type: 任务类型，如"coolpapaers", "yuanbao", "methodology"等
            provider: LLM提供商
            model: 模型名称
            stream: 是否使用流式输出
            cleanup_after_chat: 对话完成后是否清理临时文件
            
        Returns:
            模型回复或流式回复迭代器
        """
        if not self.pdf_processor.current_content:
            raise ValueError("请先加载论文并转换为Markdown")
        
        # 合并元数据和论文内容
        combined_content = self.prepare_combined_content()
        
        # 获取模型最大上下文长度并截断内容
        max_context_length = self.get_model_context_length(provider, model)
        truncated_content = self.truncate_content(combined_content, max_context_length - 500)  # 为提示词预留空间
        
        # 获取提示词模板
        template = self.prompt_config.get_prompt_template(self.prompt_type, task_type)
        if not template:
            logger.warning(f"未找到任务类型 '{task_type}' 的提示词模板，使用默认模板")
            user_message = f"请分析以下论文内容：\n\n{truncated_content}"
        else:
            # 将模板中的{text}替换为论文内容
            user_message = template.format(text=truncated_content)
        
        # 使用简化的系统提示词
        system_prompt = DEFAULT_SYSTEM_PROMPT
        
        # 调用模型
        if stream:
            response_iterator = chat(
                message=user_message,
                system_prompt=system_prompt,
                provider=provider,
                model=model,
                stream=True
            )
            
            # 流式输出时，需要在迭代器消耗完后清理
            if cleanup_after_chat:
                # 创建一个包装迭代器，在迭代完成后清理
                def wrapped_iterator():
                    try:
                        for chunk in response_iterator:
                            yield chunk
                    finally:
                        self.cleanup()
                
                return wrapped_iterator()
            else:
                return response_iterator
        else:
            response = chat(
                message=user_message,
                system_prompt=system_prompt,
                provider=provider,
                model=model,
                stream=False
            )
            
            # 清理临时文件
            if cleanup_after_chat:
                self.cleanup()
                
            return response
    
    def stream_chat_callback(
        self,
        callback: Callable[[str], None],
        task_type: str = "coolpapaers",
        provider: Optional[str] = None, 
        model: Optional[str] = None,
        cleanup_after_chat: bool = True
    ) -> None:
        """
        使用回调函数处理流式对话响应
        
        Args:
            callback: 回调函数，接收流式输出的每个部分作为参数
            task_type: 任务类型，用于选择提示词模板
            provider: LLM提供商
            model: 模型名称
            cleanup_after_chat: 对话完成后是否清理临时文件
        """
        if not self.pdf_processor.current_content:
            raise ValueError("请先加载论文并转换为Markdown")
        
        # 合并元数据和论文内容
        combined_content = self.prepare_combined_content()
        
        # 获取模型最大上下文长度并截断内容
        max_context_length = self.get_model_context_length(provider, model)
        truncated_content = self.truncate_content(combined_content, max_context_length - 500)  # 为提示词预留空间
        
        # 获取提示词模板
        template = self.prompt_config.get_prompt_template(self.prompt_type, task_type)
        if not template:
            logger.warning(f"未找到任务类型 '{task_type}' 的提示词模板，使用默认模板")
            user_message = f"请分析以下论文内容：\n\n{truncated_content}"
        else:
            # 将模板中的{text}替换为论文内容
            user_message = template.format(text=truncated_content)
        
        # 使用简化的系统提示词
        system_prompt = DEFAULT_SYSTEM_PROMPT
        
        # 调用模型与回调
        llm_stream_callback(
            message=user_message,
            callback=callback,
            system_prompt=system_prompt,
            provider=provider,
            model=model
        )
        
        # 清理临时文件
        if cleanup_after_chat:
            self.cleanup()
    
    def cleanup(self):
        """
        清理临时目录
        """
        logger.info("正在清理临时文件和目录...")
        
        # 清理临时目录
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.info(f"已删除临时目录: {temp_dir}")
            except Exception as e:
                logger.error(f"删除临时目录时出错: {e}")
        
        # 重置临时目录列表
        self.temp_dirs = []
        
        logger.info("临时文件清理完成")
    
    def close(self):
        """
        关闭资源
        """
        # 清理临时文件
        self.cleanup()
        
        # 关闭PDF处理器
        self.pdf_processor.close()
        
        # 关闭arXiv缓存
        if self.use_cache and self.arxiv_cache:
            self.arxiv_cache.close()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 便捷函数

def download_and_chat_with_paper(
    paper_id: str,
    task_type: str = "coolpapaers",
    provider: Optional[str] = None,
    model: Optional[str] = None,
    config_path: Optional[str] = None,
    image_text_mode: bool = False,
    output_dir: Optional[str] = None,
    stream: bool = False,
    stream_callback: Optional[Callable[[str], None]] = None,
    cleanup_after_chat: bool = True,
    use_cache: bool = True,
    pdf_cache_dir: Optional[str] = None,  # 重命名为 pdf_cache_dir，更清晰表明用途
    images_cache_dir: Optional[str] = None,  # 专门用于存储图片的缓存目录
    delete_rendered_images: bool = True,
    cache_base64: bool = True,
    api_key: Optional[str] = None,
    force_download: bool = False
) -> Optional[Union[str, Iterator[str]]]:
    """
    便捷函数：下载论文并与之对话
    
    Args:
        paper_id: arXiv论文ID
        task_type: 任务类型，用于选择提示词模板
        provider: LLM提供商
        model: 模型名称
        config_path: 配置文件路径
        image_text_mode: 是否使用图文模式，启用后会提取论文图片
        output_dir: 输出目录，用于存储下载的PDF和临时文件
        stream: 是否使用流式输出
        stream_callback: 流式输出回调函数
        cleanup_after_chat: 对话完成后是否清理临时文件
        use_cache: 是否使用缓存
        pdf_cache_dir: PDF解析缓存目录，用于存储PDF解析结果
        images_cache_dir: 图片缓存目录，用于存储提取的图片
        delete_rendered_images: 是否删除渲染后的页面图像
        cache_base64: 是否缓存图像的base64编码
        api_key: 图像分析API密钥
        force_download: 是否强制重新下载论文，不使用缓存
        
    Returns:
        如果stream=False或未提供stream_callback，返回模型回复或流式回复迭代器
        如果提供了stream_callback，则返回None
    """
    # 设置转换器类型和提示词类型
    converter_type = 'fitz_with_image' if image_text_mode else 'fitz'
    prompt_type = 'llm_with_image' if image_text_mode else 'llm'
    cache_namespace = 'image_paper_chat' if image_text_mode else 'text_paper_chat'
    
    # 优化：首先检查是否有缓存的论文，避免不必要的对象创建和重复下载
    pdf_path = None
    metadata = None
    
    # 如果使用缓存且不强制下载，先尝试获取缓存的PDF路径
    if use_cache and not force_download:
        arxiv_cache = PDFCache(cache_dir=pdf_cache_dir, namespace="arxiv_papers")
        try:
            cached_result = arxiv_cache.get_by_paper_id(paper_id)
            if cached_result and os.path.exists(cached_result['pdf_path']):
                logger.info(f"使用缓存的arXiv论文: {paper_id}")
                pdf_path = cached_result['pdf_path']
                # 可以重建元数据对象，但对于对话功能不是必须的
                if cached_result.get('metadata'):
                    metadata = ArxivPaper(**cached_result['metadata'])
            arxiv_cache.close()
        except Exception as e:
            logger.warning(f"检查论文缓存时出错: {e}")
    
    # 创建PDF处理器
    pdf_processor = PDFProcessor(
        converter_type=converter_type,
        cache_dir=pdf_cache_dir,  # 使用重命名的参数
        use_cache=use_cache,
        cache_namespace=cache_namespace
    )
    
    # 创建PaperChat实例
    paper_chat = PaperChat(
        config_path=config_path,
        pdf_processor=pdf_processor,
        prompt_type=prompt_type,
        cache_dir=pdf_cache_dir,
        use_cache=use_cache
    )
    
    try:
        # 如果没有获得缓存的PDF路径，则下载论文
        if not pdf_path:
            pdf_path, metadata = paper_chat.download_paper_from_arxiv(
                paper_id=paper_id, 
                output_dir=output_dir,
                force_download=force_download
            )
        else:
            # 如果已有缓存路径，直接设置当前论文元数据
            paper_chat.current_paper_metadata = metadata
        
        # 转换为Markdown
        paper_chat.convert_paper_to_markdown(
            pdf_path=pdf_path,
            strip_references=True,
            images_cache_dir=images_cache_dir,
            delete_rendered_images=delete_rendered_images,
            cache_base64=cache_base64,
            api_key=api_key
        )
        
        # 与论文对话
        if stream_callback:
            paper_chat.stream_chat_callback(
                callback=stream_callback,
                task_type=task_type,
                provider=provider,
                model=model,
                cleanup_after_chat=cleanup_after_chat
            )
            return None
        else:
            return paper_chat.chat_with_paper(
                task_type=task_type,
                provider=provider,
                model=model,
                stream=stream,
                cleanup_after_chat=cleanup_after_chat
            )
    finally:
        # 确保资源被正确释放
        if not cleanup_after_chat:
            paper_chat.close()

def chat_with_local_paper(
    pdf_path: str,
    task_type: str = "coolpapaers",
    provider: Optional[str] = None,
    model: Optional[str] = None,
    config_path: Optional[str] = None,
    image_text_mode: bool = False,
    stream: bool = False,
    stream_callback: Optional[Callable[[str], None]] = None,
    cleanup_after_chat: bool = True,
    use_cache: bool = True,
    pdf_cache_dir: Optional[str] = None,  # 重命名为 pdf_cache_dir
    images_cache_dir: Optional[str] = None,
    delete_rendered_images: bool = True,
    cache_base64: bool = True,
    api_key: Optional[str] = None
) -> Optional[Union[str, Iterator[str]]]:
    """
    便捷函数：加载本地论文并与之对话
    
    Args:
        pdf_path: 本地PDF文件路径
        task_type: 任务类型，用于选择提示词模板
        provider: LLM提供商
        model: 模型名称
        config_path: 配置文件路径
        image_text_mode: 是否使用图文模式，启用后会提取论文图片
        stream: 是否使用流式输出
        stream_callback: 流式输出回调函数
        cleanup_after_chat: 对话完成后是否清理临时文件
        use_cache: 是否使用缓存
        pdf_cache_dir: PDF解析缓存目录，用于存储PDF解析结果
        images_cache_dir: 图片缓存目录，用于存储提取的图片
        delete_rendered_images: 是否删除渲染后的页面图像
        cache_base64: 是否缓存图像的base64编码
        api_key: 图像分析API密钥
        
    Returns:
        如果stream=False或未提供stream_callback，返回模型回复或流式回复迭代器
        如果提供了stream_callback，则返回None
    """
    # 设置转换器类型和提示词类型
    converter_type = 'fitz_with_image' if image_text_mode else 'fitz'
    prompt_type = 'llm_with_image' if image_text_mode else 'llm'
    cache_namespace = 'image_paper_chat' if image_text_mode else 'text_paper_chat'
    
    # 创建PDF处理器
    pdf_processor = PDFProcessor(
        converter_type=converter_type,
        cache_dir=pdf_cache_dir,  # 使用重命名的参数
        use_cache=use_cache,
        cache_namespace=cache_namespace
    )
    
    # 创建PaperChat实例
    paper_chat = PaperChat(
        config_path=config_path,
        pdf_processor=pdf_processor,
        prompt_type=prompt_type,
        use_cache=use_cache
    )
    
    try:
        # 加载本地论文
        pdf_path = paper_chat.load_paper_from_file(pdf_path=pdf_path)
        
        # 转换为Markdown - 直接传入所有可能需要的参数
        paper_chat.convert_paper_to_markdown(
            pdf_path=pdf_path,
            strip_references=True,
            images_cache_dir=images_cache_dir,
            delete_rendered_images=delete_rendered_images,
            cache_base64=cache_base64,
            api_key=api_key
        )
        
        # 与论文对话
        if stream_callback:
            paper_chat.stream_chat_callback(
                callback=stream_callback,
                task_type=task_type,
                provider=provider,
                model=model,
                cleanup_after_chat=cleanup_after_chat
            )
            return None
        else:
            return paper_chat.chat_with_paper(
                task_type=task_type,
                provider=provider,
                model=model,
                stream=stream,
                cleanup_after_chat=cleanup_after_chat
            )
    finally:
        # 确保资源被正确释放
        if not cleanup_after_chat:
            paper_chat.close()
