import os
import yaml
from typing import Dict, Any, List, Optional


class PromptConfig:
    """
    提示词配置类，用于从prompts目录下的YAML文件加载提示词，并支持热加载和管理提示词
    """
    _instance = None  # 单例模式
    _prompts_dir = None  # 提示词目录路径

    def __new__(cls, prompts_dir=None):
        if cls._instance is None:
            cls._instance = super(PromptConfig, cls).__new__(cls)
            cls._instance._initialized = False
            # 在__new__中保存prompts_dir，确保即使在单例模式下也能使用新路径
            if prompts_dir is not None:
                cls._prompts_dir = prompts_dir
        elif prompts_dir is not None and cls._prompts_dir != prompts_dir:
            # 如果传入了新的提示词目录且与当前不同，则更新路径并重置初始化标志
            cls._prompts_dir = prompts_dir
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, prompts_dir=None):
        if self._initialized:
            return

        # 默认提示词目录路径
        if prompts_dir is None and self.__class__._prompts_dir is None:
            # 获取config_files/prompts目录
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.__class__._prompts_dir = os.path.join(current_dir, 'config_files', 'prompts')
        elif prompts_dir is not None:
            # 如果明确传入了prompts_dir，使用它覆盖类变量中的路径
            self.__class__._prompts_dir = prompts_dir

        # 初始化提示词配置字典
        self.prompts_dir = self.__class__._prompts_dir
        self.prompts = {
            'llm': {},
            'llm_with_image': {}
        }
        
        # 提示词文件名映射
        self.prompt_files = {
            'llm': 'prompts_llm.yaml',
            'llm_with_image': 'prompts_llm_with_image.yaml'
        }
        
        # 加载所有提示词
        self.reload_all()
        self._initialized = True

    def reload_all(self):
        """重新加载所有提示词文件"""
        for prompt_type, file_name in self.prompt_files.items():
            self.reload(prompt_type)

    def reload(self, prompt_type: str):
        """
        重新加载指定类型的提示词文件
        
        Args:
            prompt_type: 提示词类型，可选值为 'llm', 'llm_with_image'
        """
        if prompt_type not in self.prompt_files:
            print(f"未知的提示词类型: {prompt_type}")
            return

        file_path = os.path.join(self.prompts_dir, self.prompt_files[prompt_type])
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                self.prompts[prompt_type] = data.get('prompts', {})
            return True
        except Exception as e:
            print(f"加载提示词文件失败 {file_path}: {e}")
            # 失败时保留现有提示词
            return False

    def save(self, prompt_type: str):
        """
        保存指定类型的提示词到文件
        
        Args:
            prompt_type: 提示词类型，可选值为 'llm', 'llm_with_image'
        """
        if prompt_type not in self.prompt_files:
            print(f"未知的提示词类型: {prompt_type}")
            return False

        file_path = os.path.join(self.prompts_dir, self.prompt_files[prompt_type])
        try:
            data = {'prompts': self.prompts[prompt_type]}
                
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            print(f"保存提示词文件失败 {file_path}: {e}")
            return False

    def get_prompt(self, prompt_type: str, prompt_name: str, default: str = None) -> Optional[Dict]:
        """
        获取指定类型和名称的提示词
        
        Args:
            prompt_type: 提示词类型，可选值为 'llm', 'llm_with_image'
            prompt_name: 提示词名称
            default: 如果未找到提示词时返回的默认值
            
        Returns:
            提示词配置或默认值
        """
        if prompt_type not in self.prompts:
            return default
            
        return self.prompts[prompt_type].get(prompt_name, default)

    def get_prompt_template(self, prompt_type: str, prompt_name: str, default: str = None) -> str:
        """
        获取指定类型和名称的提示词模板
        
        Args:
            prompt_type: 提示词类型，可选值为 'llm', 'llm_with_image'
            prompt_name: 提示词名称
            default: 如果未找到提示词时返回的默认值
            
        Returns:
            提示词模板文本或默认值
        """
        prompt = self.get_prompt(prompt_type, prompt_name)
        if prompt is None:
            return default
            
        return prompt.get('template', default)

    def get_prompt_description(self, prompt_type: str, prompt_name: str, default: str = None) -> str:
        """
        获取指定类型和名称的提示词描述
        
        Args:
            prompt_type: 提示词类型，可选值为 'llm', 'llm_with_image'
            prompt_name: 提示词名称
            default: 如果未找到提示词时返回的默认值
            
        Returns:
            提示词描述或默认值
        """
        prompt = self.get_prompt(prompt_type, prompt_name)
        if prompt is None:
            return default
            
        return prompt.get('description', default)

    def set_prompt(self, prompt_type: str, prompt_name: str, template: str, 
                  description: str = None, auto_save: bool = False) -> bool:
        """
        设置或更新提示词
        
        Args:
            prompt_type: 提示词类型，可选值为 'llm', 'llm_with_image'
            prompt_name: 提示词名称
            template: 提示词模板
            description: 提示词描述
            auto_save: 是否自动保存到文件
            
        Returns:
            设置是否成功
        """
        if prompt_type not in self.prompts:
            return False
            
        # 如果提示词不存在，创建新条目
        if prompt_name not in self.prompts[prompt_type]:
            self.prompts[prompt_type][prompt_name] = {}
            
        # 更新提示词内容
        self.prompts[prompt_type][prompt_name]['template'] = template
        if description is not None:
            self.prompts[prompt_type][prompt_name]['description'] = description
            
        # 自动保存（如需要）
        if auto_save:
            return self.save(prompt_type)
        return True

    def remove_prompt(self, prompt_type: str, prompt_name: str, auto_save: bool = False) -> bool:
        """
        删除提示词
        
        Args:
            prompt_type: 提示词类型，可选值为 'llm', 'llm_with_image'
            prompt_name: 提示词名称
            auto_save: 是否自动保存到文件
            
        Returns:
            删除是否成功
        """
        if prompt_type not in self.prompts or prompt_name not in self.prompts[prompt_type]:
            return False
            
        del self.prompts[prompt_type][prompt_name]
        
        # 自动保存（如需要）
        if auto_save:
            return self.save(prompt_type)
        return True

    def list_prompts(self, prompt_type: str = None) -> Dict[str, List[str]]:
        """
        列出所有可用的提示词
        
        Args:
            prompt_type: 可选的提示词类型过滤器，为None时返回所有类型的提示词
            
        Returns:
            按类型组织的提示词名称列表的字典
        """
        result = {}
        
        if prompt_type is None:
            # 返回所有类型的提示词
            for pt in self.prompts:
                result[pt] = list(self.prompts[pt].keys())
        elif prompt_type in self.prompts:
            # 返回指定类型的提示词
            result[prompt_type] = list(self.prompts[prompt_type].keys())
            
        return result

    def format_prompt(self, prompt_type: str, prompt_name: str, **kwargs) -> Optional[str]:
        """
        格式化提示词模板，填充变量
        
        Args:
            prompt_type: 提示词类型，可选值为 'llm', 'llm_with_image'
            prompt_name: 提示词名称
            **kwargs: 要填充到模板中的变量
            
        Returns:
            格式化后的提示词，如果提示词不存在则返回None
        """
        template = self.get_prompt_template(prompt_type, prompt_name)
        if template is None:
            return None
            
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"格式化提示词模板时缺少变量: {e}")
            return None
        except Exception as e:
            print(f"格式化提示词模板失败: {e}")
            return None


# 创建默认提示词配置实例
prompt_config = PromptConfig()