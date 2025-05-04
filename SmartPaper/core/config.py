import os
import yaml
from typing import Dict, Any, List, Optional


class Config:
    """
    配置类，用于从config.yaml文件加载配置信息，并支持修改和保存配置
    """
    _instance = None  # 单例模式
    _config_path = None  # 保存配置文件路径

    def __new__(cls, config_path=None):
        # 支持通过环境变量设置配置路径

        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
            # 在__new__中保存config_path，确保即使在单例模式下也能使用新路径
            if config_path is not None:
                cls._config_path = config_path
        elif config_path is not None and cls._config_path != config_path:
            # 如果传入了新的配置路径且与当前不同，则更新路径并重置初始化标志
            cls._config_path = config_path
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path=None):
        # 支持通过环境变量设置配置路径
        env_config_path = os.environ.get('CONFIG_PATH')
        if env_config_path:
            config_path = env_config_path
            
        if self._initialized:
            return

        # 默认配置路径
        if config_path is None and self.__class__._config_path is None:
            # 首先尝试查找与应用程序同级目录下的config.yaml
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_files_dir = os.path.join(app_dir, 'config_files')
            default_paths = [
                os.path.join(config_files_dir, 'config.yaml'),  # SmartPaper/config_files/
                os.path.join(os.getcwd(), 'config.yaml'),  # 当前工作目录

                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml'),  # SmartPaper/core/
            ]
            
            for path in default_paths:
                if os.path.exists(path):
                    self.__class__._config_path = path
                    break

        elif config_path is not None:
            # 如果明确传入了config_path，使用它覆盖类变量中的路径
            self.__class__._config_path = config_path

        # 加载配置
        self.config_path = self.__class__._config_path
        self.reload()
        self._initialized = True

    def reload(self):
        """重新加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"警告: 配置文件 '{self.config_path}' 未找到，将使用默认配置")
            self.config = self._get_default_config()
            # 尝试创建配置文件目录
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            # 保存默认配置到文件
            self.save()

    def _get_default_config(self):
        """返回默认配置"""
        return {
            "llm": {
                "provider": "openai_siliconflow",
                "max_requests": 10,
                "default_model_index": 0,
                "openai_siliconflow": {
                    "api_key": "",
                    "base_url": "https://api.siliconflow.com/v1",
                    "models": [
                        {
                            "name": "Qwen/Qwen2.5-7B-Instruct",
                            "context_length": 32768  # 32k上下文窗口
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4096
                }
            },
            "document_converter": {
                "converter_name": "fitz_with_image"
            },
        }

    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项，支持使用点号分隔的路径访问嵌套配置"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any, auto_save: bool = False) -> bool:
        """
        设置配置项，支持使用点号分隔的路径设置嵌套配置
        
        Args:
            key: 配置键，支持点号分隔的多级路径
            value: 要设置的值
            auto_save: 是否自动保存到文件
        
        Returns:
            bool: 设置是否成功
        """
        keys = key.split('.')
        if not keys:
            return False
        
        # 最后一个键用于设置值
        last_key = keys.pop()
        
        # 遍历键路径，确保所有中间节点都存在
        current = self.config
        for k in keys:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        # 设置最终值
        current[last_key] = value
        
        # 自动保存（如需要）
        if auto_save:
            return self.save()
        return True

    def update(self, data: Dict[str, Any], auto_save: bool = False) -> bool:
        """
        批量更新多个配置项
        
        Args:
            data: 包含多个配置项的字典，键可以是点号分隔的路径
            auto_save: 是否自动保存到文件
        
        Returns:
            bool: 更新是否成功
        """
        success = True
        for key, value in data.items():
            if not self.set(key, value):
                success = False
        
        if success and auto_save:
            return self.save()
        return success

    # LLM配置属性和设置方法
    @property
    def llm_provider(self) -> str:
        """获取LLM提供商"""
        return self.get('llm.provider', 'openai')
    
    @llm_provider.setter
    def llm_provider(self, value: str):
        """设置LLM提供商"""
        self.set('llm.provider', value)

    @property
    def llm_config(self) -> Dict:
        """获取当前LLM提供商的配置"""
        provider = self.llm_provider
        return self.get(f'llm.{provider}', {})

    # VLM配置属性和设置方法
    @property
    def vlm_provider(self) -> str:
        """获取VLM提供商"""
        return self.get('vlm.provider', 'openai_siliconflow')
    
    @vlm_provider.setter
    def vlm_provider(self, value: str):
        """设置VLM提供商"""
        self.set('vlm.provider', value)

    @property
    def vlm_config(self) -> Dict:
        """获取当前VLM提供商的配置"""
        provider = self.vlm_provider
        return self.get(f'vlm.{provider}', {})

    # 文档转换器配置
    @property
    def document_converter(self) -> str:
        """获取文档转换器名称"""
        return self.get('document_converter.converter_name', 'fitz_with_image')
    
    @document_converter.setter
    def document_converter(self, value: str):
        """设置文档转换器名称"""
        self.set('document_converter.converter_name', value)

    # 模型配置属性和设置方法
    @property
    def models(self) -> List:
        """获取当前LLM提供商可用的模型列表"""
        models_config = self.get(f'llm.{self.llm_provider}.models', [])
        # 兼容旧格式的模型配置（纯字符串列表）和新格式（包含上下文长度的字典列表）
        if models_config and isinstance(models_config[0], dict):
            return [model.get('name') for model in models_config]
        return models_config
    
    def add_model(self, model_name: str, context_length: int = 32768, provider: str = None):
        """
        添加模型到指定提供商的模型列表
        
        Args:
            model_name: 模型名称
            context_length: 模型上下文长度
            provider: LLM提供商，默认为当前提供商
        """
        if provider is None:
            provider = self.llm_provider
        
        models = self.get(f'llm.{provider}.models', [])
        
        # 检查模型列表格式，并统一转换为新格式
        if models and isinstance(models[0], str):
            # 如果是旧格式（字符串列表），转换为新格式（字典列表）
            models = [{"name": model, "context_length": 32768} for model in models]
        
        # 检查模型是否已存在
        model_names = [model.get('name') if isinstance(model, dict) else model for model in models]
        if model_name not in model_names:
            models.append({"name": model_name, "context_length": context_length})
            self.set(f'llm.{provider}.models', models)
    
    def remove_model(self, model_name: str, provider: str = None):
        """从提供商的模型列表中移除指定模型"""
        if provider is None:
            provider = self.llm_provider
        
        models = self.get(f'llm.{provider}.models', [])
        
        # 处理不同格式的模型列表
        if models:
            if isinstance(models[0], dict):
                # 新格式（字典列表）
                models = [model for model in models if model.get('name') != model_name]
            else:
                # 旧格式（字符串列表）
                if model_name in models:
                    models.remove(model_name)
            
            self.set(f'llm.{provider}.models', models)
            
    def get_model_context_length(self, provider: str, model_name: str) -> int:
        """
        获取模型的最大上下文长度
        
        Args:
            provider: LLM提供商
            model_name: 模型名称
            
        Returns:
            模型的最大上下文长度，默认32768
        """
        models = self.get(f'llm.{provider}.models', [])
        
        # 如果模型列表为空，返回默认值
        if not models:
            return 32768
            
        # 检查模型列表格式
        if isinstance(models[0], dict):
            # 新格式（字典列表）
            for model in models:
                if model.get('name') == model_name:
                    return model.get('context_length', 32768)
        
        # 旧格式或未找到模型，返回默认值
        return 32768
    
    @property
    def default_model_index(self) -> int:
        """获取默认模型索引"""
        return self.get('llm.default_model_index', 0)
    
    @default_model_index.setter
    def default_model_index(self, value: int):
        """设置默认模型索引"""
        self.set('llm.default_model_index', value)
    
    @property
    def default_model(self) -> Optional[str]:
        """获取默认模型"""
        models = self.models
        default_index = self.default_model_index
        if models and 0 <= default_index < len(models):
            return models[default_index]
        return None if not models else models[0]

    # API相关配置属性和设置方法
    @property
    def api_key(self) -> str:
        """获取当前LLM提供商的API密钥"""
        return self.get(f'llm.{self.llm_provider}.api_key', '')
    
    @api_key.setter
    def api_key(self, value: str):
        """设置当前LLM提供商的API密钥"""
        self.set(f'llm.{self.llm_provider}.api_key', value)
    
    def set_provider_api_key(self, provider: str, api_key: str):
        """设置指定提供商的API密钥"""
        self.set(f'llm.{provider}.api_key', api_key)

    @property
    def base_url(self) -> str:
        """获取当前LLM提供商的基础URL"""
        return self.get(f'llm.{self.llm_provider}.base_url', '')
    
    @base_url.setter
    def base_url(self, value: str):
        """设置当前LLM提供商的基础URL"""
        self.set(f'llm.{self.llm_provider}.base_url', value)
    
    def set_provider_base_url(self, provider: str, base_url: str):
        """设置指定提供商的基础URL"""
        self.set(f'llm.{provider}.base_url', base_url)

    # 其他通用配置属性和设置方法
    @property
    def temperature(self) -> float:
        """获取LLM温度设置"""
        return self.get(f'llm.{self.llm_provider}.temperature', 0.7)
    
    @temperature.setter
    def temperature(self, value: float):
        """设置LLM温度"""
        self.set(f'llm.{self.llm_provider}.temperature', value)

    @property
    def max_tokens(self) -> int:
        """获取LLM最大token数"""
        return self.get(f'llm.{self.llm_provider}.max_tokens', 4096)
    
    @max_tokens.setter
    def max_tokens(self, value: int):
        """设置LLM最大token数"""
        self.set(f'llm.{self.llm_provider}.max_tokens', value)

    @property
    def max_requests(self) -> int:
        """获取最大请求次数"""
        return self.get('llm.max_requests', 10)
    
    @max_requests.setter
    def max_requests(self, value: int):
        """设置最大请求次数"""
        self.set('llm.max_requests', value)


# 创建默认配置实例
config = Config()