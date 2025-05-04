# SmartPaper 提示词配置系统使用指南

SmartPaper的提示词配置系统是基于YAML文件和Python类实现的，提供了便捷的提示词管理功能。本文档详细介绍如何使用`PromptConfig`类来加载、获取、修改和使用各种提示词模板。

## 目录

- [基本使用](#基本使用)
- [获取提示词](#获取提示词)
- [修改和创建提示词](#修改和创建提示词)
- [提示词格式化](#提示词格式化)
- [热加载机制](#热加载机制)
- [提示词文件结构](#提示词文件结构)
- [高级用法](#高级用法)
- [单例模式与参数传递](#单例模式与参数传递)
- [最佳实践](#最佳实践)

## 基本使用

`PromptConfig`类采用单例模式设计，全局只有一个实例。在导入时已经创建了默认实例，可以直接使用：

```python
# 导入预创建的提示词配置实例
from SmartPaper.core.prompt_config import prompt_config

# 获取特定类型和名称的提示词模板
template = prompt_config.get_prompt_template('llm', 'coolpapaers')

# 使用提示词模板（填充变量）
formatted_prompt = prompt_config.format_prompt('llm', 'coolpapaers', text="论文内容...")
```

## 获取提示词

### 查看所有可用提示词

```python
# 列出所有类型的提示词
all_prompts = prompt_config.list_prompts()
print(all_prompts)
# 输出: {'llm': ['coolpapaers', 'yuanbao', ...], 'llm_with_image': [...]}

# 列出特定类型的提示词
llm_prompts = prompt_config.list_prompts('llm')
print(llm_prompts)
# 输出: {'llm': ['coolpapaers', 'yuanbao', ...]}
```

### 获取提示词内容

```python
# 获取完整的提示词配置（包括模板和描述）
prompt = prompt_config.get_prompt('llm', 'coolpapaers')

# 只获取提示词模板
template = prompt_config.get_prompt_template('llm', 'coolpapaers')

# 只获取提示词描述
description = prompt_config.get_prompt_description('llm', 'coolpapaers')

# 使用默认值（当提示词不存在时）
template = prompt_config.get_prompt_template('llm', 'non_existent', default='默认模板')
```

## 修改和创建提示词

### 创建或更新提示词

```python
# 创建新提示词
prompt_config.set_prompt(
    prompt_type='llm',
    prompt_name='new_paper_analysis',
    template="请分析以下论文：\n\n{text}\n\n重点关注...",
    description="新的论文分析提示词"
)

# 修改现有提示词
prompt_config.set_prompt(
    prompt_type='llm', 
    prompt_name='coolpapaers',
    template="新的提示词模板\n\n{text}"
)

# 创建并自动保存到文件
prompt_config.set_prompt(
    prompt_type='llm',
    prompt_name='quick_summary',
    template="简要总结以下论文：\n\n{text}",
    description="快速论文总结",
    auto_save=True  # 自动保存到文件
)
```

### 删除提示词

```python
# 删除提示词
prompt_config.remove_prompt('llm', 'unused_prompt')

# 删除并自动保存到文件
prompt_config.remove_prompt('llm', 'unused_prompt', auto_save=True)
```

### 保存修改

如果没有使用`auto_save=True`选项，需要手动调用`save`方法将修改保存到文件：

```python
# 修改提示词后保存
prompt_config.set_prompt('llm', 'coolpapaers', "新模板")
result = prompt_config.save('llm')  # 保存llm类型的提示词

if result:
    print("提示词已成功保存")
else:
    print("保存提示词时出错")
```

## 提示词格式化

提示词格式化是将模板中的占位符替换为实际值的过程：

```python
# 基本格式化
formatted = prompt_config.format_prompt(
    prompt_type='llm', 
    prompt_name='coolpapaers', 
    text="这是一篇关于深度学习的论文..."
)

# 多个变量格式化
formatted = prompt_config.format_prompt(
    prompt_type='llm',
    prompt_name='custom_template',
    title="生成式AI的最新进展",
    author="张三",
    year="2025",
    abstract="本文探讨了生成式AI的最新技术发展和应用场景..."
)
```

### 格式化效果示例

假设我们有以下提示词模板：

```yaml
prompts:
  custom_template:
    description: "自定义多变量模板"
    template: |
      # {title}
      
      作者: {author}
      发表年份: {year}
      
      ## 摘要
      
      {abstract}
      
      ## 分析报告
      
      这篇由{author}在{year}年发表的论文《{title}》主要内容是：
      {abstract}
      
      以下是详细分析...
```

使用上面的多变量格式化代码后，实际生成的提示词将如下所示：

```
# 生成式AI的最新进展

作者: 张三
发表年份: 2025

## 摘要

本文探讨了生成式AI的最新技术发展和应用场景...

## 分析报告

这篇由张三在2025年发表的论文《生成式AI的最新进展》主要内容是：
本文探讨了生成式AI的最新技术发展和应用场景...

以下是详细分析...
```

这种多变量格式化方式非常灵活，可以根据需要在提示词的不同位置插入各类变量，使生成的提示词更加个性化和针对性强。

格式化会根据提示词模板中的占位符（如`{text}`, `{title}`, `{author}`）自动填充对应的值。

## 热加载机制

热加载机制允许在程序运行时重新从文件加载提示词配置，适用于配置文件被外部修改的情况：

```python
# 重新加载所有提示词文件
prompt_config.reload_all()

# 重新加载特定类型的提示词文件
prompt_config.reload('llm')
prompt_config.reload('llm_with_image')
```

这在以下情况特别有用：
- 开发过程中直接修改YAML文件来测试不同的提示词
- 由其他程序或用户修改了提示词配置文件
- 需要在不重启应用的情况下应用新的提示词

## 提示词文件结构

提示词配置文件(`prompts_*.yaml`)的基本结构如下：

### 大语言模型提示词 (prompts_llm.yaml)

```yaml
prompts:
  coolpapaers:  # 提示词名称
    description: "复刻 papers.cool"  # 提示词描述
    template: |  # 提示词模板
      请仔细分析论文内容，并回答如下问题：
      
      Q: 这篇论文是什么？
      概括该论文是做什么的。
      
      # ... 模板内容 ...
      
      {text}  # 占位符，会被实际内容替换
  
  yuanbao:
    description: "类似混元元宝总结"
    template: |
      请分析以下论文内容，提供一个全面的总结分析，包括：
      # ... 模板内容 ...
      {text}
```

### 带图像的大语言模型提示词 (prompts_llm_with_image.yaml)

```yaml
prompts:
  coolpapaers:
    description: "复刻 papers.cool(带图版)"
    template: |
      你可以使用markdown格式来组织你的回答。
      # ... 模板内容 ...
      {text}
```

## 高级用法

### 使用自定义提示词目录

可以在创建配置实例时指定自定义提示词目录：

```python
from SmartPaper.core.prompt_config import PromptConfig

# 使用自定义提示词目录路径
custom_prompt_config = PromptConfig("/path/to/custom/prompts")
```

### 定制提示词文件名映射

如果需要使用不同的文件名模式，可以修改提示词文件名映射：

```python
from SmartPaper.core.prompt_config import PromptConfig

custom_config = PromptConfig()
custom_config.prompt_files = {
    'llm': 'custom_llm_prompts.yaml',
    'llm_with_image': 'custom_visual_prompts.yaml'
}
custom_config.reload_all()  # 使用新的文件名重新加载
```

## 单例模式与参数传递

`PromptConfig`类使用单例模式，确保全局只有一个提示词配置实例。但它支持在不同时刻传入不同的提示词目录路径：

```python
# 首次创建实例，使用默认提示词目录
config1 = PromptConfig()

# 稍后创建实例，但使用不同的提示词目录
config2 = PromptConfig("/path/to/another/prompts/directory")
```

即使是单例模式，当传入新的提示词目录路径时，配置类会执行以下行为：
1. 检查新路径是否与当前路径不同
2. 如果不同，更新提示词目录路径并重置初始化标志
3. 从新路径加载提示词文件

这样的设计使得可以在运行时切换提示词目录，例如：

```python
# 一般情况下使用默认提示词配置
from SmartPaper.core.prompt_config import prompt_config

# 某些情况下需要使用特定的提示词目录
def use_special_prompts():
    # 这会使全局prompt_config实例切换到新的提示词目录
    special_config = PromptConfig("/path/to/special/prompts")
    
    # 进行一些操作...
    
    # 恢复为默认提示词配置
    default_config = PromptConfig()  # 会重新加载默认提示词目录
```

注意：使用这种方式切换提示词目录会影响所有使用该配置实例的代码，所以要谨慎使用。

## 最佳实践

1. **使用单例实例**: 尽量使用预创建的`prompt_config`实例，而不是创建新实例。

   ```python
   # 推荐
   from SmartPaper.core.prompt_config import prompt_config
   
   # 不推荐（除非有特殊需求）
   from SmartPaper.core.prompt_config import PromptConfig
   new_config = PromptConfig()
   ```

2. **提示词模板设计**:
   - 使用清晰的变量名称作为占位符 (例如 `{text}`, `{title}`)
   - 为复杂提示词添加注释，解释预期的输入和输出
   - 考虑提示词可能的变体和用例

3. **错误处理**: 检查格式化和保存操作的返回值，处理可能的失败情况。

   ```python
   formatted = prompt_config.format_prompt('llm', 'template', text="内容")
   if formatted is None:
       print("格式化提示词失败，请检查模板和参数")
   
   if not prompt_config.save('llm'):
       print("保存提示词失败，请检查文件权限")
   ```

4. **组织提示词**:
   - 按功能或用例对提示词进行分组
   - 使用一致的命名约定
   - 提供详细的描述，说明每个提示词的用途和预期效果

5. **定期备份**: 重要的提示词配置应定期备份，避免意外丢失。

---

通过本指南，你应该能够轻松地在SmartPaper项目中使用提示词配置系统，包括读取、修改和应用各种提示词模板。如有任何问题，请参考`PromptConfig`类的源代码或联系项目维护人员。