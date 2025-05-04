import os
import sys
import pytest
import yaml
import tempfile
import shutil
import io
import contextlib

# 添加项目根目录到sys.path，确保可以导入SmartPaper模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from SmartPaper.core.prompt_config import PromptConfig

class TestPromptConfig:

    @pytest.fixture
    def real_prompts_dir(self):
        """使用真实的提示词文件路径"""
        # 获取测试数据文件所在的路径
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        test_data_dir = os.path.join(current_dir, 'test_datas')
        
        # 确保测试数据文件存在
        assert os.path.exists(test_data_dir), f"测试数据目录不存在: {test_data_dir}"
        assert os.path.exists(os.path.join(test_data_dir, 'prompts_llm.yaml')), "提示词文件不存在"
        assert os.path.exists(os.path.join(test_data_dir, 'prompts_llm_with_image.yaml')), "提示词图像文件不存在"
        
        return test_data_dir

    @pytest.fixture
    def temp_prompts_dir(self):
        """创建临时的提示词目录供测试使用"""
        temp_dir = tempfile.mkdtemp()
        
        # 获取测试数据文件所在的路径
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        test_data_dir = os.path.join(current_dir, 'test_datas')
        
        # 复制测试文件到临时目录
        shutil.copy(
            os.path.join(test_data_dir, 'prompts_llm.yaml'),
            os.path.join(temp_dir, 'prompts_llm.yaml')
        )
        
        shutil.copy(
            os.path.join(test_data_dir, 'prompts_llm_with_image.yaml'),
            os.path.join(temp_dir, 'prompts_llm_with_image.yaml')
        )
        
        yield temp_dir
        
        # 测试结束后清理
        shutil.rmtree(temp_dir)
    
    def test_singleton_pattern(self, temp_prompts_dir):
        """测试单例模式"""
        config1 = PromptConfig(temp_prompts_dir)
        config2 = PromptConfig()
        
        assert config1 is config2
        assert config1.prompts_dir == temp_prompts_dir
        assert config2.prompts_dir == temp_prompts_dir

    def test_different_directory(self, temp_prompts_dir):
        """测试使用不同目录初始化时的行为"""
        config1 = PromptConfig(temp_prompts_dir)
        
        new_dir = tempfile.mkdtemp()
        try:
            config2 = PromptConfig(new_dir)
            
            # 应该是同一个实例但路径已更新
            assert config1 is config2
            assert config1.prompts_dir == new_dir
            assert config2.prompts_dir == new_dir
        finally:
            shutil.rmtree(new_dir)

    def test_reload_all(self, temp_prompts_dir):
        """测试重新加载所有提示词"""
        config = PromptConfig(temp_prompts_dir)
        
        # 清空当前提示词
        config.prompts = {'llm': {}, 'llm_with_image': {}}
        
        # 重新加载所有
        config.reload_all()
        
        # 检查是否加载成功
        assert 'coolpapaers' in config.prompts['llm']
        assert 'yuanbao' in config.prompts['llm_with_image']

    def test_get_prompt(self, real_prompts_dir):
        """测试获取提示词"""
        config = PromptConfig(real_prompts_dir)
        
        # 获取存在的提示词
        prompt = config.get_prompt('llm', 'coolpapaers')
        assert prompt is not None
        assert 'template' in prompt
        assert 'description' in prompt
        assert prompt['description'] == "复刻 papers.cool"
        
        # 获取不存在的提示词，使用默认值
        default_value = {'template': 'default'}
        prompt = config.get_prompt('llm', 'non_existent', default=default_value)
        assert prompt == default_value
        
        # 获取不存在类型的提示词
        prompt = config.get_prompt('invalid_type', 'test_prompt', default='default')
        assert prompt == 'default'

    def test_get_prompt_template(self, real_prompts_dir):
        """测试获取提示词模板"""
        config = PromptConfig(real_prompts_dir)
        
        template = config.get_prompt_template('llm', 'coolpapaers')
        assert template is not None
        assert "请仔细分析论文内容" in template
        
        # 测试默认值
        template = config.get_prompt_template('llm', 'non_existent', default='default template')
        assert template == 'default template'

    def test_get_prompt_description(self, real_prompts_dir):
        """测试获取提示词描述"""
        config = PromptConfig(real_prompts_dir)
        
        description = config.get_prompt_description('llm', 'coolpapaers')
        assert description == "复刻 papers.cool"
        
        description = config.get_prompt_description('llm_with_image', 'coolpapaers')
        assert description == "复刻 papers.cool(带图版)"
        
        # 测试默认值
        description = config.get_prompt_description('llm', 'non_existent', default='default description')
        assert description == 'default description'

    def test_set_prompt(self, temp_prompts_dir):
        """测试设置提示词"""
        config = PromptConfig(temp_prompts_dir)
        
        # 新增提示词
        result = config.set_prompt('llm', 'new_prompt', 'New template {var}', 'New description')
        assert result is True
        
        # 验证新增的提示词
        prompt = config.get_prompt('llm', 'new_prompt')
        assert prompt['template'] == 'New template {var}'
        assert prompt['description'] == 'New description'
        
        # 更新已有提示词
        result = config.set_prompt('llm', 'coolpapaers', 'Updated template {var}')
        assert result is True
        
        # 验证更新的提示词
        template = config.get_prompt_template('llm', 'coolpapaers')
        assert template == 'Updated template {var}'
        # 描述应保持不变
        description = config.get_prompt_description('llm', 'coolpapaers')
        assert description == "复刻 papers.cool"
        
        # 测试无效类型
        result = config.set_prompt('invalid_type', 'prompt', 'template')
        assert result is False

    def test_set_prompt_with_auto_save(self, temp_prompts_dir):
        """测试设置提示词并自动保存"""
        config = PromptConfig(temp_prompts_dir)
        
        result = config.set_prompt('llm', 'auto_save_prompt', 'Auto save template', 'Auto save description', auto_save=True)
        assert result is True
        
        # 创建新实例强制重新加载文件
        new_config = PromptConfig.__new__(PromptConfig)
        new_config.__init__(temp_prompts_dir)
        
        # 验证是否成功保存到文件
        prompt = new_config.get_prompt('llm', 'auto_save_prompt')
        assert prompt is not None
        assert prompt['template'] == 'Auto save template'

    def test_remove_prompt(self, temp_prompts_dir):
        """测试删除提示词"""
        config = PromptConfig(temp_prompts_dir)
        
        # 删除现有提示词
        result = config.remove_prompt('llm', 'coolpapaers')
        assert result is True
        
        # 验证删除结果
        prompt = config.get_prompt('llm', 'coolpapaers')
        assert prompt is None
        
        # 删除不存在的提示词
        result = config.remove_prompt('llm', 'non_existent')
        assert result is False
        
        # 删除无效类型的提示词
        result = config.remove_prompt('invalid_type', 'prompt')
        assert result is False

    def test_list_prompts(self, real_prompts_dir):
        """测试列出提示词"""
        config = PromptConfig(real_prompts_dir)
        
        # 列出特定类型的提示词
        prompts = config.list_prompts('llm')
        assert 'llm' in prompts
        assert 'coolpapaers' in prompts['llm']
        assert 'yuanbao' in prompts['llm']
        assert 'llm_with_image' not in prompts
        
        # 列出所有类型的提示词
        all_prompts = config.list_prompts()
        assert 'llm' in all_prompts
        assert 'llm_with_image' in all_prompts
        assert 'coolpapaers' in all_prompts['llm']
        assert 'methodology' in all_prompts['llm_with_image']
        
        # 列出无效类型的提示词
        invalid_prompts = config.list_prompts('invalid_type')
        assert 'invalid_type' not in invalid_prompts

    def test_format_prompt(self, real_prompts_dir):
        """测试格式化提示词"""
        config = PromptConfig(real_prompts_dir)
        
        # 获取示例提示词模板以便测试格式化
        full_analysis_template = config.get_prompt_template('llm', 'full_analysis')
        test_text = "这是一篇测试论文。"
        
        # 格式化有效提示词
        formatted = config.format_prompt('llm', 'full_analysis', text=test_text)
        assert formatted is not None
        assert test_text in formatted
        
        # 格式化不存在的提示词
        formatted = config.format_prompt('llm', 'non_existent')
        assert formatted is None
        
        # 格式化时缺少必要变量
        # 使用contextlib.redirect_stdout捕获print输出而不是使用pytest.warns
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture):
            formatted = config.format_prompt('llm', 'full_analysis')
            # 由于格式化失败，应该返回None
            assert formatted is None
            
        # 验证输出信息中包含预期的错误信息
        stdout_content = stdout_capture.getvalue()
        assert '格式化提示词模板时缺少变量' in stdout_content
        assert "'text'" in stdout_content
