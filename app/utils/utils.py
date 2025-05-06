"""
工具函数

提供API服务所需的各种工具函数
"""

import os
import uuid
import logging
import json
from typing import Dict, Any, Optional, List, Iterator
from pathlib import Path

from SmartPaper.core.config import Config
from SmartPaper.core.prompt_config import PromptConfig

# 导入图片处理函数
from app.utils.llm_output_postprocess import find_and_replace_image_in_stream

# 配置日志
logger = logging.getLogger(__name__)

# 初始化配置管理器
config = Config()

# 初始化提示词配置
prompt_config = PromptConfig()

def generate_file_id() -> str:
    """生成唯一文件ID"""
    return str(uuid.uuid4())


def ensure_directory(directory: str) -> None:
    """确保目录存在"""
    os.makedirs(directory, exist_ok=True)


def get_upload_path() -> str:
    """获取上传文件的存储目录"""
    # 默认存储在项目根目录下的uploads文件夹
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    ensure_directory(upload_dir)
    return upload_dir


def save_uploaded_file(file_content: bytes, file_name: str) -> Dict[str, Any]:
    """
    保存上传的文件
    
    Args:
        file_content: 文件内容
        file_name: 文件名
    
    Returns:
        包含文件ID和路径的字典
    """
    file_id = generate_file_id()
    upload_dir = get_upload_path()
    
    # 使用文件ID作为文件名前缀，避免文件名冲突
    safe_filename = f"{file_id}_{file_name}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return {
            "file_id": file_id,
            "file_path": file_path,
            "success": True
        }
    except Exception as e:
        logger.error(f"保存上传文件失败: {e}")
        return {
            "file_id": file_id,
            "file_path": "",
            "success": False,
            "error": str(e)
        }


def format_sse_message(data: Dict[str, Any]) -> str:
    """
    格式化SSE消息
    
    Args:
        data: 要发送的数据
    
    Returns:
        格式化后的SSE消息
    """
    json_data = json.dumps(data, ensure_ascii=False)
    return f"data: {json_data}\n\n"


class SSEStreamer:
    """SSE流式响应助手类"""
    
    @staticmethod
    def stream_generator(text_iterator: Iterator[str]) -> Iterator[str]:
        """
        将文本迭代器转换为SSE流
        
        Args:
            text_iterator: 文本块迭代器
        
        Yields:
            格式化的SSE消息
        """
        try:
            for chunk in text_iterator:
                if chunk:
                    yield format_sse_message({
                        "content": chunk,
                        "done": False
                    })
            
            # 发送结束信号
            yield format_sse_message({
                "content": "",
                "done": True
            })
        except Exception as e:
            logger.error(f"流式生成出错: {e}")
            # 发送错误信息
            yield format_sse_message({
                "content": f"生成过程中出现错误: {str(e)}",
                "done": True,
                "error": str(e)
            })
    
    @staticmethod
    def stream_generator_with_image_processing(
        text_iterator: Iterator[str],
        images_cache_dir: str
    ) -> Iterator[str]:
        """
        将文本迭代器转换为SSE流，并处理其中的图片引用
        
        Args:
            text_iterator: 文本块迭代器
            images_cache_dir: 图片缓存目录
        
        Yields:
            格式化的SSE消息，图片引用被替换为base64编码
        """
        try:
            # 图片引用处理状态
            img_ref_buffer = ""
            collecting_img_ref = False
            
            for chunk in text_iterator:
                if chunk:
                    # 处理图片引用
                    processed_chunk, img_ref_buffer, collecting_img_ref = find_and_replace_image_in_stream(
                        chunk, 
                        img_ref_buffer, 
                        collecting_img_ref,
                        images_cache_dir
                    )
                    
                    # 只有当处理后的块有内容时才发送
                    if processed_chunk:
                        yield format_sse_message({
                            "content": processed_chunk,
                            "done": False
                        })
            
            # 如果还有未处理完的图片引用，作为普通文本发送
            if img_ref_buffer:
                yield format_sse_message({
                    "content": img_ref_buffer,
                    "done": False
                })
            
            # 发送结束信号
            yield format_sse_message({
                "content": "",
                "done": True
            })
        except Exception as e:
            logger.error(f"流式生成出错: {e}")
            # 发送错误信息
            yield format_sse_message({
                "content": f"生成过程中出现错误: {str(e)}",
                "done": True,
                "error": str(e)
            })


def get_providers_info() -> Dict[str, Any]:
    """
    获取所有提供商和模型信息
    
    Returns:
        包含提供商和模型信息的字典
    """
    try:
        # 重新加载配置以确保获取最新信息
        config.reload()
        
        # 获取配置中的LLM部分
        llm_config = config.config.get('llm', {})
        
        # 获取默认提供商
        default_provider = llm_config.get('provider', 'openai_siliconflow')
        
        # 获取默认模型索引和模型
        default_model_index = llm_config.get('default_model_index', 0)
        default_model = None
        
        # 准备提供商列表
        providers = []
        
        # 遍历配置中的所有提供商
        for key, value in llm_config.items():
            # 跳过非提供商配置项
            if key in ['provider', 'default_model_index', 'max_requests']:
                continue
                
            if not isinstance(value, dict):
                continue
                
            # 获取提供商信息
            provider_info = {
                'name': key,
                'models': [],
                'base_url': value.get('base_url', ''),
                'temperature': value.get('temperature', 0.7),
                'max_tokens': value.get('max_tokens', 4096)
            }
            
            # 获取模型列表
            models_config = value.get('models', [])
            
            # 处理可能的不同模型格式
            models = []
            if models_config:
                if isinstance(models_config[0], dict):
                    # 新格式（字典列表）
                    for model in models_config:
                        models.append({
                            'name': model.get('name', ''),
                            'context_length': model.get('context_length', 32768)
                        })
                else:
                    # 旧格式（字符串列表）
                    for model_name in models_config:
                        models.append({
                            'name': model_name,
                            'context_length': 32768  # 默认值
                        })
            
            provider_info['models'] = models
            providers.append(provider_info)
            
            # 如果是默认提供商，设置默认模型
            if key == default_provider and models:
                if 0 <= default_model_index < len(models):
                    default_model = models[default_model_index].get('name') if isinstance(models[default_model_index], dict) else models[default_model_index]
                else:
                    default_model = models[0].get('name') if isinstance(models[0], dict) else models[0]
        
        return {
            'providers': providers,
            'default_provider': default_provider,
            'default_model': default_model,
            'success': True
        }
    except Exception as e:
        logger.error(f"获取提供商信息失败: {e}")
        return {
            'providers': [],
            'default_provider': '',
            'default_model': None,
            'success': False,
            'error': str(e)
        }

def update_config(update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新配置
    
    Args:
        update_data: 要更新的配置数据
        
    Returns:
        更新结果
    """
    try:
        # 获取目标提供商
        target_provider = update_data.get('target_provider')
        if not target_provider:
            target_provider = config.llm_provider
            
        # 更新默认提供商
        if 'provider' in update_data and update_data['provider']:
            config.llm_provider = update_data['provider']
            
        # 更新默认模型索引
        if 'default_model_index' in update_data and update_data['default_model_index'] is not None:
            config.default_model_index = update_data['default_model_index']
            
        # 更新API密钥
        if 'api_key' in update_data and update_data['api_key'] is not None:
            config.set_provider_api_key(target_provider, update_data['api_key'])
            
        # 更新基础URL
        if 'base_url' in update_data and update_data['base_url']:
            config.set_provider_base_url(target_provider, update_data['base_url'])
            
        # 更新温度参数
        if 'temperature' in update_data and update_data['temperature'] is not None:
            config.set(f'llm.{target_provider}.temperature', update_data['temperature'])
            
        # 更新最大token数
        if 'max_tokens' in update_data and update_data['max_tokens'] is not None:
            config.set(f'llm.{target_provider}.max_tokens', update_data['max_tokens'])
        
        # 保存配置
        success = config.save()
        
        return {
            'success': success,
            'error': None if success else "保存配置失败"
        }
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def reload_config() -> Dict[str, Any]:
    """
    重新加载配置
    
    Returns:
        重载结果
    """
    try:
        config.reload()
        return {
            'success': True
        }
    except Exception as e:
        logger.error(f"重新加载配置失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_prompt_list(prompt_type: Optional[str] = None) -> Dict[str, Any]:
    """
    获取提示词列表
    
    Args:
        prompt_type: 可选的提示词类型过滤器
        
    Returns:
        提示词列表
    """
    try:
        prompts = prompt_config.list_prompts(prompt_type)
        return {
            "prompts": prompts,
            "success": True
        }
    except Exception as e:
        logger.error(f"获取提示词列表失败: {e}")
        return {
            "prompts": {},
            "success": False,
            "error": str(e)
        }

def get_prompt_detail(prompt_type: str, prompt_name: str) -> Dict[str, Any]:
    """
    获取提示词详情
    
    Args:
        prompt_type: 提示词类型，如llm或llm_with_image
        prompt_name: 提示词名称
        
    Returns:
        提示词详情
    """
    try:
        template = prompt_config.get_prompt_template(prompt_type, prompt_name)
        description = prompt_config.get_prompt_description(prompt_type, prompt_name)
        
        if template is None:
            return {
                "success": False,
                "error": f"未找到提示词: {prompt_type}/{prompt_name}"
            }
            
        return {
            "template": template,
            "description": description,
            "success": True
        }
    except Exception as e:
        logger.error(f"获取提示词详情失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def update_prompt(prompt_type: str, prompt_name: str, template: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    更新或创建提示词
    
    Args:
        prompt_type: 提示词类型，如llm或llm_with_image
        prompt_name: 提示词名称
        template: 提示词模板
        description: 提示词描述
        
    Returns:
        更新结果
    """
    try:
        success = prompt_config.set_prompt(prompt_type, prompt_name, template, description, auto_save=True)
        
        if not success:
            return {
                "success": False,
                "error": "更新提示词失败"
            }
            
        return {
            "success": True
        }
    except Exception as e:
        logger.error(f"更新提示词失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def delete_prompt(prompt_type: str, prompt_name: str) -> Dict[str, Any]:
    """
    删除提示词
    
    Args:
        prompt_type: 提示词类型，如llm或llm_with_image
        prompt_name: 提示词名称
        
    Returns:
        删除结果
    """
    try:
        success = prompt_config.remove_prompt(prompt_type, prompt_name, auto_save=True)
        
        if not success:
            return {
                "success": False,
                "error": f"删除提示词失败，可能不存在: {prompt_type}/{prompt_name}"
            }
            
        return {
            "success": True
        }
    except Exception as e:
        logger.error(f"删除提示词失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def reload_prompts() -> Dict[str, Any]:
    """
    重新加载提示词配置
    
    Returns:
        重载结果
    """
    try:
        prompt_config.reload_all()
        return {
            "success": True
        }
    except Exception as e:
        logger.error(f"重新加载提示词失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }
