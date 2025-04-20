import os
from typing import Dict
import yaml
from loguru import logger
import os
from typing import Union, Optional


class PromptLibrary:
    def __init__(self, prompt_file: Optional[str] = None):
        """初始化提示词库

        Args:
            prompt_file (str): 提示词配置文件路径
        """
        if prompt_file is None:
            # 获取项目根目录的绝对路径
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.prompt_file = os.path.join(root_dir, "config", "prompts_llm.yaml")
        else:
            self.prompt_file = prompt_file

        self.prompts = self._load_prompts()
        logger.info(f"成功加载了 {len(self.prompts)} 个提示词模板")

    def _load_prompts(self) -> Dict:
        """加载提示词配置

        Returns:
            Dict: 提示词配置
        """
        try:
            with open(self.prompt_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config["prompts"]
        except Exception as e:
            raise Exception(f"加载提示词配置失败: {str(e)}")

    def get_prompt(self, prompt_name: str) -> str:
        """获取指定名称的提示词模板

        Args:
            prompt_name (str): 提示词名称

        Returns:
            str: 提示词模板
        """
        if prompt_name not in self.prompts:
            raise ValueError(f"未找到名为 '{prompt_name}' 的提示词模板")
        return self.prompts[prompt_name]["template"]

    def list_prompts(self) -> Dict[str, str]:
        """列出所有可用的提示词模板

        Returns:
            Dict[str, str]: 提示词名称和描述的字典
        """
        return {name: info["description"] for name, info in self.prompts.items()}

    def reload(self):
        """重新加载提示词配置"""
        self.prompts = self._load_prompts()


# 创建全局实例
_prompt_library = PromptLibrary()


# 导出便捷函数
def get_prompt(prompt_name: str) -> str:
    """获取指定名称的提示词模板

    Args:
        prompt_name (str): 提示词名称

    Returns:
        str: 提示词模板
    """
    return _prompt_library.get_prompt(prompt_name)


def list_prompts() -> Dict[str, str]:
    """列出所有可用的提示词模板

    Returns:
        Dict[str, str]: 提示词名称和描述的字典
    """
    return _prompt_library.list_prompts()


def reload_prompts():
    """重新加载提示词配置"""
    _prompt_library.reload()
