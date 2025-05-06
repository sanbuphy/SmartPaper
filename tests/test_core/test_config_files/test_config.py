import os
import sys
import pytest
import tempfile
import shutil
import yaml

# 添加项目根目录到sys.path，确保可以导入SmartPaper模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from SmartPaper.core.config import Config


# 测试前准备和清理的 fixture
@pytest.fixture
def config_paths():
    """创建临时配置文件和测试路径，用于测试"""
    # 使用 tests/test_datas/config.example.yaml 作为测试配置文件
    test_config_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', 'test_datas', 'config.example.yaml'
    ))
    
    # 创建一个临时目录用于测试保存功能
    temp_dir = tempfile.mkdtemp()
    temp_config_path = os.path.join(temp_dir, 'temp_config.yaml')
    
    # 复制测试配置文件到临时目录
    with open(test_config_path, 'r', encoding='utf-8') as src_file:
        test_config_content = src_file.read()
        with open(temp_config_path, 'w', encoding='utf-8') as dest_file:
            dest_file.write(test_config_content)
    
    # 重置Config的单例状态，以便每个测试都使用干净的状态
    Config._instance = None
    Config._config_path = None
    
    # 返回需要的路径
    yield {"test_config_path": test_config_path, "temp_config_path": temp_config_path, "temp_dir": temp_dir}
    
    # 清理工作
    Config._instance = None
    Config._config_path = None
    
    # 删除临时目录及其内容
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_singleton_pattern(config_paths):
    """测试单例模式是否正常工作"""
    config1 = Config(config_paths["test_config_path"])
    config2 = Config(config_paths["test_config_path"])
    
    # 验证两个实例是同一个对象
    assert config1 is config2, "单例模式测试失败，应该返回同一个实例"


def test_singleton_with_different_paths(config_paths):
    """测试使用不同路径时单例的行为"""
    # 第一次使用test_config_path
    config1 = Config(config_paths["test_config_path"])
    assert config1.config_path == config_paths["test_config_path"]
    
    # 第二次使用temp_config_path，应该更新路径并重新加载
    config2 = Config(config_paths["temp_config_path"])
    assert config1 is config2, "应该仍然是同一个实例"
    assert config2.config_path == config_paths["temp_config_path"], "应该更新配置路径"


def test_load_config(config_paths):
    """测试加载配置文件"""
    config = Config(config_paths["test_config_path"])
    
    # 验证基本配置项是否正确加载
    assert config.llm_provider == "openai_siliconflow"
    assert config.max_requests == 10
    assert config.document_converter == "fitz_with_image"


def test_get_method(config_paths):
    """测试get方法获取配置项"""
    config = Config(config_paths["test_config_path"])
    
    # 测试获取现有配置
    assert config.get("llm.provider") == "openai_siliconflow"
    assert config.get("llm.max_requests") == 10
    
    # 测试获取嵌套配置
    openai_api_key = config.get("llm.openai.api_key")
    assert openai_api_key == ""  # 更新为空字符串
    
    # 测试获取不存在的配置项，使用默认值
    assert config.get("non_existent_key", "default_value") == "default_value"
    assert config.get("llm.non_existent_key", 123) == 123


def test_property_getters(config_paths):
    """测试属性访问器"""
    config = Config(config_paths["test_config_path"])
    
    # 测试基本属性访问器
    assert config.llm_provider == "openai_siliconflow"
    assert config.vlm_provider == "openai_siliconflow"
    assert config.document_converter == "fitz_with_image"
    
    # 测试API键和URL属性访问器
    assert config.api_key == ""  # 更新为空字符串
    assert config.base_url == "https://api.siliconflow.com/v1"
    
    # 测试模型相关属性访问器
    models = config.models
    expected_models = [
        "Qwen/Qwen2.5-72B-Instruct", 
        "Qwen/Qwen2.5-72B-Instruct-128K",
        "Qwen/Qwen2.5-7B-Instruct", 
        "Qwen/Qwen2.5-32B-Instruct"
    ]
    assert set(models) == set(expected_models)
    assert config.default_model == models[0]
    
    # 测试其他通用属性
    assert config.temperature == 0.7
    assert config.max_tokens == 4096


def test_property_setters(config_paths):
    """测试属性设置器"""
    config = Config(config_paths["temp_config_path"])  # 使用临时配置文件以便修改
    
    # 测试设置基本属性
    config.llm_provider = "openai"
    assert config.llm_provider == "openai"
    
    # 测试设置API键
    config.api_key = "new-api-key"
    assert config.get("llm.openai.api_key") == "new-api-key"
    
    # 测试设置温度和最大token
    config.temperature = 0.5
    config.max_tokens = 2048
    assert config.temperature == 0.5
    assert config.max_tokens == 2048


def test_set_method(config_paths):
    """测试set方法设置配置项"""
    config = Config(config_paths["temp_config_path"])  # 使用临时配置文件以便修改
    
    # 测试设置简单配置项
    config.set("llm.provider", "zhipuai")
    assert config.llm_provider == "zhipuai"
    
    # 测试设置嵌套配置项
    config.set("llm.zhipuai.api_key", "new-zhipu-api-key")
    assert config.get("llm.zhipuai.api_key") == "new-zhipu-api-key"
    
    # 测试设置新的配置项（之前不存在）
    config.set("new_section.new_key", "new_value")
    assert config.get("new_section.new_key") == "new_value"


def test_update_method(config_paths):
    """测试update方法批量更新配置项"""
    config = Config(config_paths["temp_config_path"])  # 使用临时配置文件以便修改
    
    # 准备批量更新的配置
    update_data = {
        "llm.provider": "openai",
        "llm.openai.api_key": "updated-api-key",
        "llm.max_requests": 20,
        "document_converter.converter_name": "fitz"
    }
    
    # 执行批量更新
    success = config.update(update_data)
    assert success is True, "批量更新应该成功"
    
    # 验证更新后的配置
    assert config.llm_provider == "openai"
    assert config.get("llm.openai.api_key") == "updated-api-key"
    assert config.max_requests == 20
    assert config.document_converter == "fitz"


def test_save_method(config_paths):
    """测试save方法保存配置到文件"""
    config = Config(config_paths["temp_config_path"])  # 使用临时配置文件以便修改
    
    # 修改一些配置
    config.llm_provider = "openai"
    config.api_key = "saved-api-key"
    config.set("new_section.test_key", "test_value")
    
    # 保存配置
    result = config.save()
    assert result is True, "保存配置应该成功"
    
    # 重新加载配置，验证修改是否已保存
    config.reload()
    assert config.llm_provider == "openai"
    assert config.get("llm.openai.api_key") == "saved-api-key"
    assert config.get("new_section.test_key") == "test_value"
    
    # 直接读取文件内容进行验证
    with open(config_paths["temp_config_path"], 'r', encoding='utf-8') as f:
        loaded_config = yaml.safe_load(f)
        assert loaded_config["llm"]["provider"] == "openai"
        assert loaded_config["llm"]["openai"]["api_key"] == "saved-api-key"
        assert loaded_config["new_section"]["test_key"] == "test_value"


def test_auto_save(config_paths):
    """测试auto_save参数的功能"""
    config = Config(config_paths["temp_config_path"])  # 使用临时配置文件以便修改
    
    # 使用set方法的auto_save参数
    config.set("llm.provider", "zhipuai", auto_save=True)
    
    # 重新加载配置，验证更改是否已保存
    config_reloaded = Config(config_paths["temp_config_path"])
    assert config_reloaded.llm_provider == "zhipuai"
    
    # 使用update方法的auto_save参数
    config.update({
        "llm.provider": "openai",
        "document_converter.converter_name": "fitz"
    }, auto_save=True)
    
    # 重新加载配置，验证更改是否已保存
    config_reloaded = Config(config_paths["temp_config_path"])
    assert config_reloaded.llm_provider == "openai"
    assert config_reloaded.document_converter == "fitz"


def test_add_remove_model(config_paths):
    """测试添加和删除模型"""
    config = Config(config_paths["temp_config_path"])
    
    # 记录原始模型数量
    original_models = config.models.copy()
    original_count = len(original_models)
    
    # 添加新模型，使用新格式（包含上下文长度）
    new_model = "gpt-4-vision-preview"
    config.add_model(new_model, context_length=128000, provider="openai")
    
    # 验证模型是否已添加
    openai_models = config.get("llm.openai.models")
    
    # 检查添加的模型
    model_names = [model['name'] if isinstance(model, dict) else model for model in openai_models]
    assert new_model in model_names
    
    # 测试获取上下文长度
    context_length = config.get_model_context_length("openai", new_model)
    assert context_length == 128000
    
    # 移除模型
    config.remove_model(new_model, provider="openai")
    
    # 验证模型是否已移除
    openai_models = config.get("llm.openai.models")
    model_names = [model['name'] if isinstance(model, dict) else model for model in openai_models]
    assert new_model not in model_names
    
    # 对当前提供商进行测试
    current_provider = config.llm_provider
    test_model_name = "new-model"
    config.add_model(test_model_name)  # 不指定提供商，应该添加到当前提供商
    
    updated_models = config.models
    assert len(updated_models) == len(original_models) + 1
    assert test_model_name in updated_models


# 添加新的测试函数以测试模型上下文长度功能
def test_model_context_length(config_paths):
    """测试模型上下文长度的获取和设置"""
    config = Config(config_paths["temp_config_path"])
    
    # 创建不同格式的测试数据
    # 1. 测试旧格式的模型列表（字符串）
    old_format_provider = "old_format_provider"
    old_format_models = ["model1", "model2", "model3"]
    config.set(f"llm.{old_format_provider}.models", old_format_models)
    
    # 使用默认上下文长度获取结果
    context_length = config.get_model_context_length(old_format_provider, "model1")
    assert context_length == 32768  # 默认值
    
    # 2. 测试新格式的模型列表（字典）
    new_format_provider = "new_format_provider"
    new_format_models = [
        {"name": "model1", "context_length": 16384},
        {"name": "model2", "context_length": 32768},
        {"name": "model3", "context_length": 128000}
    ]
    config.set(f"llm.{new_format_provider}.models", new_format_models)
    
    # 测试从新格式获取上下文长度
    context_length1 = config.get_model_context_length(new_format_provider, "model1")
    assert context_length1 == 16384
    
    context_length3 = config.get_model_context_length(new_format_provider, "model3")
    assert context_length3 == 128000
    
    # 测试未知模型
    unknown_context = config.get_model_context_length(new_format_provider, "unknown_model")
    assert unknown_context == 32768  # 默认值


def test_provider_specific_methods(config_paths):
    """测试提供商特定的方法"""
    config = Config(config_paths["temp_config_path"])
    
    # 设置特定提供商的API密钥
    config.set_provider_api_key("zhipuai", "zhipu-specific-key")
    assert config.get("llm.zhipuai.api_key") == "zhipu-specific-key"
    
    # 设置特定提供商的base_url
    config.set_provider_base_url("openai_kimi", "https://custom-kimi-api.com/v1")
    assert config.get("llm.openai_kimi.base_url") == "https://custom-kimi-api.com/v1"


def test_default_model(config_paths):
    """测试默认模型的获取和设置"""
    config = Config(config_paths["temp_config_path"])
    
    # 在测试前确保模型列表被正确加载
    # 如果测试配置使用新格式，先转换为可比较的格式
    models = config.models
    
    # 获取当前默认模型
    default_model = config.default_model
    assert default_model == models[0]  # 默认是第一个模型
    
    # 更改默认模型索引
    config.default_model_index = 1
    assert config.default_model_index == 1
    assert config.default_model == models[1]
    
    # 设置超出范围的索引
    config.default_model_index = 100
    # 当索引超出范围时，应该返回第一个模型
    assert config.default_model == models[0]






# pytest 的参数化测试示例
@pytest.mark.parametrize("provider,expected_key", [
    ("openai", ""),
    ("openai_siliconflow", ""),
    ("zhipuai", ""),
    ("ai_studio", "01ada502"),
    ("ai_studio_fast_deploy", "01ad5a502"),
])
def test_provider_api_keys(config_paths, provider, expected_key):
    """测试不同提供商的API密钥获取"""
    config = Config(config_paths["test_config_path"])
    assert config.get(f"llm.{provider}.api_key") == expected_key


@pytest.mark.parametrize("provider,expected_url", [
    ("openai", "https://api.openai.com/v1"),
    ("openai_siliconflow", "https://api.siliconflow.com/v1"),
    ("openai_deepseek", "https://api.deepseek.com/v1"),
    ("openai_kimi", "https://api.moonshot.cn/v1"),
    ("ai_studio", "https://aistudio.baidu.com/llm/lmapi/v3"),
    ("openai_aistudio", "https://api.baidu.com/v1"),
    ("openai_doubao", "https://ark.cn-beijing.volces.com/api/v3"),
    ("ai_studio_fast_deploy", "https://api-f6f9v9xdo8n0j2yd.aistudio-app.com/v1")
])
def test_provider_base_urls(config_paths, provider, expected_url):
    """测试不同提供商的基础URL获取"""
    config = Config(config_paths["test_config_path"])
    assert config.get(f"llm.{provider}.base_url") == expected_url


def test_vlm_config(config_paths):
    """测试VLM配置的获取"""
    config = Config(config_paths["test_config_path"])
    
    # 测试VLM提供商
    assert config.vlm_provider == "openai_siliconflow"
    
    # 测试VLM API密钥
    assert config.get("vlm.openai_siliconflow.api_key") == ""
    
    # 测试VLM模型
    vlm_models = config.get("vlm.openai_siliconflow.models")
    assert isinstance(vlm_models, list)
    expected_vlm_models = [
        "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
        "Qwen/Qwen2.5-VL-32B-Instruct",
        "Qwen/Qwen2.5-VL-72B-Instruct",
        "Qwen/Qwen2-VL-72B-Instruct",
        "Qwen/Qwen2-VL-7B-Instruct"
    ]
    model_names = [model['name'] if isinstance(model, dict) else model for model in vlm_models]
    assert set(model_names) == set(expected_vlm_models)