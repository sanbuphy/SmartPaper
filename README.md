<div align="center">
  <img src="assets/logo.png" alt="SmartPaper Logo" width="200"/>
  <p><b>智能论文阅读与分析助手</b></p>

  <!-- 项目徽章 -->
  <a href="https://github.com/sanbuphy/SmartPaper/stargazers"><img src="https://img.shields.io/github/stars/sanbuphy/SmartPaper?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/sanbuphy/SmartPaper/network/members"><img src="https://img.shields.io/github/forks/sanbuphy/SmartPaper?style=flat-square" alt="Forks"></a>
  <a href="https://github.com/sanbuphy/SmartPaper/issues"><img src="https://img.shields.io/github/issues/sanbuphy/SmartPaper?style=flat-square" alt="Issues"></a>
  <a href="https://github.com/sanbuphy/SmartPaper/blob/main/LICENSE"><img src="https://img.shields.io/github/license/sanbuphy/SmartPaper?style=flat-square" alt="License"></a>
  <a href="https://github.com/sanbuphy/SmartPaper/pulls"><img src="https://img.shields.io/github/issues-pr/sanbuphy/SmartPaper?style=flat-square" alt="Pull Requests"></a>
  <a href="https://github.com/sanbuphy/SmartPaper/commits"><img src="https://img.shields.io/github/last-commit/sanbuphy/SmartPaper?style=flat-square" alt="Last Commit"></a>
</div>

<p align="center">
  <b>📑 快速分析论文 | 🧠 多模型支持 | 📊 结构化输出 | 🔌 易于扩展</b>
</p>
<p align="center">
  <a href="#-功能特点">功能特点</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-高级配置">高级配置</a> •
  <a href="#-示例展示">示例展示</a> •
  <a href="#-参与贡献">参与贡献</a> •
  <a href="#-许可证">许可证</a>
</p>

---

## 📖 项目简介

**SmartPaper** 是一个领先的智能论文阅读和分析工具，通过集成多种大语言模型 (LLM) 接口，自动分析学术论文内容并生成高质量的结构化报告。无论您是研究人员、学生还是对最新研究感兴趣的专业人士，SmartPaper 都能帮助您更高效地理解和提炼复杂的学术内容。

> **注意**：项目当前处于高速迭代阶段，API 可能会发生变动。架构稳定后将尽量避免核心代码变更。

## ✨ 功能特点

### 📱 多模型支持
- **国内外主流大模型**：
  - 文心一言大模型
  - OpenAI (GPT系列)
  - Deepseek
  - SiliconFlow
  - Kimi (Moonshot)
  - 豆包 (Doubao)
  - 智谱AI

### 📄 灵活输入
- **多种输入方式**：
  - 单个 PDF 文件分析
  - PDF 文件夹批量处理
  - 论文 URL（支持 arXiv 格式自动转换和验证）

### 🧠 智能分析
- **多种分析模式**：
  - **单提示词模式**：使用精心设计的提示词模板高效分析
  - **Agent 模式**：智能对话式深度分析（开发中）

### 🖥️ 用户友好
- **多种交互方式**：
  - 命令行工具（标准模式和流式输出模式）
  - 基于 Streamlit 的直观图形界面

### 📊 结构化输出
- **多样化输出格式**：
  - Markdown 格式报告
  - CSV 格式 (开发中)
  - 结构化文件夹输出 (开发中)

### 🔌 高度可定制
- 自定义提示词模板（支持文本和图像分析）
- 灵活的请求策略与限制保护
- 可扩展的文档转换器系统（[查看注册指南](docs/register_document_converter.md)）

## 🚀 快速开始

### 1. 安装

#### 方法一：开发模式安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/sanbuphy/SmartPaper.git
cd SmartPaper

# 开发模式安装
pip install -e .
```

#### 方法二：从 requirements.txt 安装

```bash
git clone https://github.com/sanbuphy/SmartPaper.git
cd SmartPaper
pip install -r requirements.txt
```

#### Python 3.10 以下 markitdown 兼容性解决方案

```bash
# 卸载之前安装的 markitdown
pip uninstall markitdown
git clone https://github.com/jingsongliujing/markitdown.git
cd markitdown
pip install -e packages/markitdown
```

### 2. 配置

创建并编辑配置文件：

```bash
cp config/config.yaml.example config/config.yaml
```

在 `config.yaml` 中配置 API 密钥和其他设置：

```yaml
openai_deepseek:
  api_key: "your-api-key"
  base_url: "https://api.deepseek.com/v1"
  model: "deepseek-chat"
  temperature: 0.7
  max_tokens: 8192
```

### 3. 使用

#### 命令行分析论文

```bash
# 使用默认提示词模板分析指定论文
python cli_get_prompt_mode_paper.py https://arxiv.org/pdf/2312.12456.pdf

# 指定提示词模板
python cli_get_prompt_mode_paper.py https://arxiv.org/pdf/2312.12456.pdf -p coolpapaers

# 流式输出模式
python cli_get_prompt_mode_paper_stream.py https://arxiv.org/pdf/2312.12456.pdf
```

#### 启动图形界面

```bash
streamlit run streamlit.app.py
```

## 📚 详细文档

### 命令行工具

项目提供两种命令行交互方式：

1. **标准模式** (`cli_get_prompt_mode_paper.py`)
   - 一次性分析并输出结果
   - 适合快速分析场景

   ```bash
   python cli_get_prompt_mode_paper.py [论文URL] --prompt [模板名称]
   ```

2. **流式模式** (`cli_get_prompt_mode_paper_stream.py`)
   - 实时显示分析进度和结果
   - 适合长文档分析

   ```bash
   python cli_get_prompt_mode_paper_stream.py [论文URL] --prompt [模板名称]
   ```

### 图形界面使用流程

1. 启动 Streamlit 应用
2. 在侧边栏选择 LLM 提供商和分析模式
3. 输入论文 URL 或上传 PDF 文件
4. 选择提示词模板
5. 点击"开始分析"按钮
6. 实时查看分析进度和结果
7. 下载分析报告或进行新的分析

### 提示词模板

| 模板名称 | 描述 |
|---------|------|
| `yuanbao` | 类似混元元宝的总结风格，包含研究背景、方法、实验设计和结果分析 |
| `coolpapaers` | 类似 papers.cool 的分析风格，包含问题定义、相关研究、解决方案、实验和未来方向 |
| `methodology` | 专注于研究方法论分析 |
| `results` | 专注于实验结果分析 |
| `contribution` | 专注于主要贡献分析 |
| `full_analysis` | 全面深入的分析 |
| `description_image` | VLM模板：图像内容描述 |
| `ocr_image` | VLM模板：OCR图像到Markdown的转换 |

## 🔧 高级配置

### 配置文件详解

查看完整配置说明：[配置文件使用说明](docs/config_yaml_guide.md)

主要配置项包括：
- LLM 提供商设置
- API 请求参数
- 请求限制策略
- 输出格式选项
- 模板定制选项

### 自定义文档转换器

SmartPaper 支持自定义文档转换器，方便处理各种特定格式的文档。
详情请参阅：[文档转换器注册指南](docs/register_document_converter.md)

## 📊 示例展示

### 分析报告示例

```markdown
# 论文分析报告

## 元数据
- 标题: Transformer-Based Visual Segmentation: A Survey
- 作者: Zhang et al.
- URL: https://arxiv.org/pdf/2304.09854.pdf
- 分析时间: 2024-05-15T14:30:00

## 研究背景
本文是一篇关于基于Transformer的视觉分割技术的综述论文。视觉分割是计算机视觉中的基本任务，包括语义分割、实例分割和全景分割等。随着Transformer在自然语言处理领域取得突破性进展，研究人员开始将其应用于视觉分割任务，并取得了显著成果。

## 核心方法
论文系统地回顾了基于Transformer的视觉分割方法，将其分为四类：
1. **纯Transformer架构**：完全基于自注意力机制的方法
2. **CNN-Transformer混合架构**：结合CNN和Transformer优势的方法
3. **轻量级Transformer**：针对资源受限场景的高效实现
4. **特定任务的创新**：针对特定分割任务的专门设计

## 实验结果
论文对比了各类方法在主流基准测试上的性能，包括Cityscapes、ADE20K等数据集。结果表明：
- 纯Transformer模型在高分辨率图像上表现优异
- 混合架构在平衡精度和效率方面表现良好
- 轻量级设计在移动设备上取得了实用性能

## 未来方向
1. 更高效的注意力机制设计
2. 自监督学习与Transformer分割的结合
3. 针对特定领域的专用模型优化
4. 模型可解释性研究
```

### 图形界面预览

![SmartPaper GUI](docs/assets/smartpaper_gui_preview.png)

## 🧪 测试

SmartPaper 提供完整的测试套件，确保功能正常工作：

```bash
# 运行所有测试
python run_tests.py

# 运行特定类别的测试
python run_tests.py --category core     # 核心功能测试
python run_tests.py --category tools    # 工具类测试
python run_tests.py --category integration   # 集成测试

# 运行特定的测试文件
python run_tests.py --file test_paper_url.py

# 显示详细测试信息
python run_tests.py --verbose
```

更多测试相关信息，请参阅 [tests/README.md](tests/README.md)。

## 📅 开发路线图

- [ ] Agent 模式增强
- [ ] CSV 格式结构化输出
- [ ] 结构化文件夹输出
- [ ] 支持更多论文来源和格式
- [ ] 批量处理优化
- [ ] 进度可视化改进
- [ ] 可视化提示词模板编辑器
- [ ] 跨平台桌面应用支持
- [ ] 国际化支持

## 🤝 参与贡献

我们非常欢迎和感谢各种形式的贡献！

### 贡献流程

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

### 代码规范

本项目使用 pre-commit 进行代码质量控制：

```bash
# 安装 pre-commit
pip install pre-commit
pre-commit install

# 首次检查所有文件
pre-commit run --all-files
```

每次提交代码时，pre-commit 将自动检查修改的文件，确保符合项目代码规范。

### 提交 Issue

- 使用 Issue 模板报告 bug
- 提出新功能建议
- 讨论项目的整体方向

## 🌟 贡献者

感谢以下贡献者为项目做出的宝贵贡献：

<div align="center">
  <a href="https://github.com/sanbuphy/SmartPaper">
    <img src="https://contrib.rocks/image?repo=sanbuphy/SmartPaper" />
  </a>
</div>

- [散步](https://github.com/sanbuphy) (Datawhale成员)
- [筱可](https://github.com/li-xiu-qi) (datawhale应用发烧友)
- [jingsongliujing](https://github.com/jingsongliujing)

## 📜 许可证

本项目采用 [Apache 许可证 2.0](LICENSE) 进行许可。
