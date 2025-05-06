import os
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SmartPaper.core.chat_with_paper import PaperChat, PDFProcessor, download_and_chat_with_paper, chat_with_local_paper
from SmartPaper.get_arxiv.arxiv_client import ArxivPaper


class TestPDFProcessor(unittest.TestCase):
    """测试PDF处理器"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp(prefix="test_pdf_processor_")
        self.test_pdf_path = os.path.join(self.temp_dir, "test.pdf")
        # 创建一个空的测试PDF文件
        with open(self.test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n')
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('SmartPaper.core.chat_with_paper.convert_pdf_to_markdown')
    def test_process_pdf(self, mock_convert):
        """测试处理PDF的基本功能"""
        # 设置模拟返回值
        mock_convert.return_value = "# 测试文档\n\n这是测试内容"
        
        # 创建PDF处理器实例
        processor = PDFProcessor(converter_type='fitz', use_cache=False)
        
        # 处理PDF
        result = processor.process_pdf(
            pdf_path=self.test_pdf_path,
            output_dir=self.temp_dir
        )
        
        # 验证调用和结果
        self.assertEqual(result, "# 测试文档\n\n这是测试内容")
        mock_convert.assert_called_once_with(
            pdf_path=self.test_pdf_path,
            output_dir=self.temp_dir,
            converter_type='fitz',
            strip_references=True
        )
        self.assertEqual(processor.current_content, "# 测试文档\n\n这是测试内容")
        self.assertEqual(processor.current_pdf_path, self.test_pdf_path)
        
        # 测试清理功能
        processor.close()
        self.assertIsNone(processor.current_content)
        self.assertIsNone(processor.current_pdf_path)
    
    @patch('SmartPaper.core.chat_with_paper.PDFCache')
    @patch('SmartPaper.core.chat_with_paper.convert_pdf_to_markdown')
    def test_process_pdf_with_cache(self, mock_convert, mock_cache_class):
        """测试使用缓存处理PDF"""
        # 设置模拟对象
        mock_cache = MagicMock()
        mock_cache_class.return_value = mock_cache
        mock_cache.get.return_value = None  # 第一次缓存未命中
        mock_convert.return_value = "# 缓存测试\n\n这是缓存测试内容"
        
        # 创建PDF处理器实例，启用缓存
        processor = PDFProcessor(converter_type='fitz', use_cache=True)
        
        # 处理PDF
        result = processor.process_pdf(self.test_pdf_path)
        
        # 验证缓存操作
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once_with(
            pdf_path=self.test_pdf_path,
            converter_type='fitz',
            params={'strip_references': True},
            result="# 缓存测试\n\n这是缓存测试内容"
        )
        
        # 模拟第二次调用时缓存命中
        mock_cache.get.return_value = "# 缓存命中\n\n这是从缓存获取的内容"
        mock_convert.reset_mock()
        
        # 再次处理相同的PDF
        result2 = processor.process_pdf(self.test_pdf_path)
        
        # 验证使用了缓存结果，且没有再次调用转换函数
        self.assertEqual(result2, "# 缓存命中\n\n这是从缓存获取的内容")
        mock_convert.assert_not_called()
        
        # 测试关闭会调用缓存关闭方法    
        processor.close()
        mock_cache.close.assert_called_once()


class TestPaperChat(unittest.TestCase):
    """测试论文对话类"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp(prefix="test_paper_chat_")
        self.test_pdf_path = os.path.join(self.temp_dir, "test_paper.pdf")
        # 创建一个空的测试PDF文件
        with open(self.test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n')
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('SmartPaper.core.chat_with_paper.ModelManager')
    def test_init(self, mock_model_manager_class):
        """测试初始化功能"""
        mock_model_manager = MagicMock()
        mock_model_manager_class.return_value = mock_model_manager
        
        # 创建模拟PDF处理器
        mock_pdf_processor = MagicMock()
        
        # 初始化PaperChat
        chat = PaperChat(
            pdf_processor=mock_pdf_processor,
            image_text_mode=True,
            prompt_type='custom_prompt'
        )
        
        # 验证初始化结果
        self.assertEqual(chat.prompt_type, 'custom_prompt')
        self.assertEqual(chat.pdf_processor, mock_pdf_processor)
        self.assertEqual(chat.conversation_history, [])
        self.assertEqual(chat.temp_dirs, [])
        self.assertIsNone(chat.current_paper_metadata)
    
    @patch('SmartPaper.core.chat_with_paper.download_paper')
    def test_download_paper_from_arxiv(self, mock_download):
        """测试从arXiv下载论文"""
        # 创建测试数据
        mock_metadata = MagicMock(spec=ArxivPaper)
        mock_metadata.title = "测试论文"
        mock_metadata.authors = ["测试作者"]
        mock_metadata.published = datetime.now()
        mock_metadata.categories = ["cs.AI"]
        mock_metadata.abstract = "这是测试摘要"
        
        # 设置模拟返回值
        mock_download.return_value = (self.test_pdf_path, mock_metadata)
        
        # 创建PaperChat实例
        chat = PaperChat(pdf_processor=MagicMock())
        
        # 测试下载论文
        pdf_path, metadata = chat.download_paper_from_arxiv("1234.5678")
        
        # 验证结果
        self.assertEqual(pdf_path, self.test_pdf_path)
        self.assertEqual(metadata, mock_metadata)
        self.assertEqual(chat.current_paper_metadata, mock_metadata)
        mock_download.assert_called_once_with(
            paper_id="1234.5678",
            output_dir=ANY,
            get_metadata=True
        )
        
        # 验证临时目录跟踪
        self.assertEqual(len(chat.temp_dirs), 1)
    
    def test_load_paper_from_file(self):
        """测试从本地文件加载论文"""
        chat = PaperChat(pdf_processor=MagicMock())
        
        # 测试加载论文
        pdf_path = chat.load_paper_from_file(self.test_pdf_path)
        
        # 验证结果
        self.assertEqual(pdf_path, self.test_pdf_path)
        self.assertIsNone(chat.current_paper_metadata)
        
        # 测试加载不存在的文件
        with self.assertRaises(FileNotFoundError):
            chat.load_paper_from_file("不存在的文件.pdf")
    
    def test_convert_paper_to_markdown(self):
        """测试将论文转换为Markdown"""
        mock_pdf_processor = MagicMock()
        mock_pdf_processor.process_pdf.return_value = "# 转换结果\n\n这是转换后的内容"
        
        chat = PaperChat(pdf_processor=mock_pdf_processor)
        
        # 测试转换论文
        result = chat.convert_paper_to_markdown(
            pdf_path=self.test_pdf_path,
            output_dir=self.temp_dir,
            strip_references=True,
            custom_param="test"
        )
        
        # 验证结果
        self.assertEqual(result, "# 转换结果\n\n这是转换后的内容")
        mock_pdf_processor.process_pdf.assert_called_once_with(
            pdf_path=self.test_pdf_path,
            output_dir=self.temp_dir,
            strip_references=True,
            custom_param="test"
        )
    
    @patch('SmartPaper.core.chat_with_paper.chat')
    def test_chat_with_paper(self, mock_chat):
        """测试与论文对话"""
        # 设置模拟对象
        mock_pdf_processor = MagicMock()
        mock_pdf_processor.current_content = "这是论文内容"
        
        mock_prompt_config = MagicMock()
        mock_prompt_config.get_prompt_template.return_value = "系统提示: {text}"
        
        mock_chat.return_value = "这是模型的回复"
        
        # 创建PaperChat实例并替换提示词配置
        chat = PaperChat(pdf_processor=mock_pdf_processor)
        chat.prompt_config = mock_prompt_config
        chat.current_paper_metadata = MagicMock()
        chat.current_paper_metadata.title = "测试论文"
        chat.current_paper_metadata.authors = ["作者1", "作者2"]
        chat.current_paper_metadata.categories = ["cs.AI"]
        chat.current_paper_metadata.published = datetime.now()
        
        # 测试对话
        result = chat.chat_with_paper(
            user_query="测试问题",
            task_type="test_task",
            cleanup_after_chat=False
        )
        
        # 验证结果
        self.assertEqual(result, "这是模型的回复")
        self.assertEqual(len(chat.conversation_history), 2)  # 一个用户问题，一个模型回复
        self.assertEqual(chat.conversation_history[0]["role"], "user")
        self.assertEqual(chat.conversation_history[0]["content"], "测试问题")
        self.assertEqual(chat.conversation_history[1]["role"], "assistant")
        self.assertEqual(chat.conversation_history[1]["content"], "这是模型的回复")
        
        # 验证提示词处理
        mock_prompt_config.get_prompt_template.assert_called_once_with(chat.prompt_type, "test_task")
        
        # 验证调用聊天API
        mock_chat.assert_called_once()
        args, kwargs = mock_chat.call_args
        self.assertIn("请根据提供的论文内容，回答以下问题：\n测试问题", kwargs["message"])
        self.assertIn("系统提示:", kwargs["system_prompt"])
        self.assertFalse(kwargs["stream"])
    
    @patch('SmartPaper.core.chat_with_paper.llm_stream_callback')
    def test_stream_chat_callback(self, mock_stream_callback):
        """测试使用回调函数的流式对话"""
        # 设置模拟对象
        mock_pdf_processor = MagicMock()
        mock_pdf_processor.current_content = "这是论文内容"
        
        mock_prompt_config = MagicMock()
        mock_prompt_config.get_prompt_template.return_value = "系统提示: {text}"
        
        # 模拟流式回调函数调用
        def side_effect(message, callback, system_prompt, **kwargs):
            callback("流式回复第1部分")
            callback("流式回复第2部分")
            callback("流式回复第3部分")
        
        mock_stream_callback.side_effect = side_effect
        
        # 创建PaperChat实例并替换提示词配置
        chat = PaperChat(pdf_processor=mock_pdf_processor)
        chat.prompt_config = mock_prompt_config
        chat.current_paper_metadata = None  # 测试没有元数据的情况
        
        # 创建测试回调函数
        collected_responses = []
        def test_callback(chunk):
            collected_responses.append(chunk)
        
        # 测试流式对话
        chat.stream_chat_callback(
            user_query="流式测试问题",
            callback=test_callback,
            cleanup_after_chat=False
        )
        
        # 验证回调函数收集的结果
        self.assertEqual(collected_responses, ["流式回复第1部分", "流式回复第2部分", "流式回复第3部分"])
        
        # 验证对话历史
        self.assertEqual(len(chat.conversation_history), 2)
        self.assertEqual(chat.conversation_history[0]["role"], "user")
        self.assertEqual(chat.conversation_history[0]["content"], "流式测试问题")
        self.assertEqual(chat.conversation_history[1]["role"], "assistant")
        self.assertEqual(chat.conversation_history[1]["content"], "流式回复第1部分流式回复第2部分流式回复第3部分")
        
        # 验证流式回调API调用
        mock_stream_callback.assert_called_once()
        args, kwargs = mock_stream_callback.call_args
        self.assertIn("请根据提供的论文内容，回答以下问题：\n流式测试问题", kwargs["message"])
        self.assertIn("系统提示:", kwargs["system_prompt"])
    
    def test_cleanup(self):
        """测试清理临时目录"""
        # 创建测试临时目录
        temp_dir1 = tempfile.mkdtemp(prefix="test_cleanup1_")
        temp_dir2 = tempfile.mkdtemp(prefix="test_cleanup2_")
        
        # 创建PaperChat实例
        chat = PaperChat(pdf_processor=MagicMock())
        
        # 添加临时目录
        chat.temp_dirs = [temp_dir1, temp_dir2]
        
        # 测试清理功能
        chat.cleanup()
        
        # 验证临时目录已被删除
        self.assertFalse(os.path.exists(temp_dir1))
        self.assertFalse(os.path.exists(temp_dir2))
        self.assertEqual(chat.temp_dirs, [])


class TestConvenienceFunctions(unittest.TestCase):
    """测试便捷函数"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp(prefix="test_convenience_")
        self.test_pdf_path = os.path.join(self.temp_dir, "test_paper.pdf")
        # 创建一个空的测试PDF文件
        with open(self.test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n')
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('SmartPaper.core.chat_with_paper.PaperChat')
    def test_download_and_chat_with_paper(self, mock_paper_chat_class):
        """测试下载并与论文对话的便捷函数"""
        # 设置模拟对象
        mock_paper_chat = MagicMock()
        mock_paper_chat_class.return_value = mock_paper_chat
        mock_paper_chat.download_paper_from_arxiv.return_value = (self.test_pdf_path, MagicMock())
        mock_paper_chat.chat_with_paper.return_value = "模型回复"
        
        # 测试普通对话
        result = download_and_chat_with_paper(
            paper_id="1234.5678",
            user_query="测试问题",
            image_text_mode=True,
            provider="test_provider",
            model="test_model",
            pdf_cache_dir="/path/to/pdf_cache",
            images_cache_dir="/path/to/images_cache"
        )
        
        # 验证结果
        self.assertEqual(result, "模型回复")
        
        # 验证创建了合适的PDF处理器
        mock_paper_chat_class.assert_called_once()
        args, kwargs = mock_paper_chat_class.call_args
        self.assertEqual(kwargs["prompt_type"], "llm_with_image")
        
        # 验证调用了下载和对话方法
        mock_paper_chat.download_paper_from_arxiv.assert_called_once_with(
            paper_id="1234.5678",
            output_dir=None
        )
        
        mock_paper_chat.convert_paper_to_markdown.assert_called_once()
        convert_args, convert_kwargs = mock_paper_chat.convert_paper_to_markdown.call_args
        self.assertEqual(convert_kwargs["pdf_path"], self.test_pdf_path)
        self.assertTrue(convert_kwargs["strip_references"])
        self.assertEqual(convert_kwargs["images_cache_dir"], "/path/to/images_cache")  # 修改为images_cache_dir
        
        mock_paper_chat.chat_with_paper.assert_called_once_with(
            user_query="测试问题",
            task_type="coolpapaers",
            provider="test_provider",
            model="test_model",
            stream=False,
            cleanup_after_chat=True
        )
        
        # 验证调用了关闭方法
        mock_paper_chat.close.assert_not_called()  # 因为cleanup_after_chat=True
        
        # 重置模拟对象
        mock_paper_chat_class.reset_mock()
        mock_paper_chat.reset_mock()
        
        # 测试流式回调函数
        callback = MagicMock()
        result = download_and_chat_with_paper(
            paper_id="1234.5678",
            user_query="测试问题",
            stream_callback=callback,
            cleanup_after_chat=False
        )
        
        # 验证使用了流式回调
        self.assertIsNone(result)
        mock_paper_chat.stream_chat_callback.assert_called_once_with(
            user_query="测试问题",
            callback=callback,
            task_type="coolpapaers",
            provider=None,
            model=None,
            cleanup_after_chat=False
        )
        mock_paper_chat.close.assert_called_once()  # 因为cleanup_after_chat=False
    
    @patch('SmartPaper.core.chat_with_paper.PaperChat')
    def test_chat_with_local_paper(self, mock_paper_chat_class):
        """测试与本地论文对话的便捷函数"""
        # 设置模拟对象
        mock_paper_chat = MagicMock()
        mock_paper_chat_class.return_value = mock_paper_chat
        mock_paper_chat.load_paper_from_file.return_value = self.test_pdf_path
        mock_paper_chat.chat_with_paper.return_value = "本地论文回复"
        
        # 测试与本地论文对话
        result = chat_with_local_paper(
            pdf_path=self.test_pdf_path,
            user_query="本地测试问题",
            task_type="local_test",
            image_text_mode=True,
            provider="local_provider",
            model="local_model",
            pdf_cache_dir="/path/to/pdf_cache",
            images_cache_dir="/path/to/images_cache"
        )
        
        # 验证结果
        self.assertEqual(result, "本地论文回复")
        
        # 验证加载和转换方法调用
        mock_paper_chat.load_paper_from_file.assert_called_once_with(pdf_path=self.test_pdf_path)
        
        mock_paper_chat.convert_paper_to_markdown.assert_called_once()
        convert_args, convert_kwargs = mock_paper_chat.convert_paper_to_markdown.call_args
        self.assertEqual(convert_kwargs["pdf_path"], self.test_pdf_path)
        self.assertTrue(convert_kwargs["strip_references"])
        self.assertEqual(convert_kwargs["images_cache_dir"], "/path/to/images_cache")  # 修改为images_cache_dir
        self.assertIn("delete_rendered_images", convert_kwargs)
        
        # 验证对话方法调用
        mock_paper_chat.chat_with_paper.assert_called_once_with(
            user_query="本地测试问题",
            task_type="local_test",
            provider="local_provider",
            model="local_model",
            stream=False,
            cleanup_after_chat=True
        )


if __name__ == "__main__":
    # 示例使用方式
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 使用流式输出的样例函数
    def print_stream(chunk):
        print(chunk, end="", flush=True)
    
    # 使用纯文本版本
    print("\n=== 纯文本论文对话示例 ===\n")
    # 创建纯文本PDF处理器
    text_processor = PDFProcessor(converter_type='fitz', use_cache=True)
    with PaperChat(pdf_processor=text_processor) as paper_chat:
        # 下载论文
        pdf_path, _ = paper_chat.download_paper_from_arxiv("1706.03762")  # Transformer论文
        
        # 转换为Markdown
        paper_chat.convert_paper_to_markdown(
            pdf_path=pdf_path,
            strip_references=True
        )
        
        # 使用提示词模板
        paper_chat.stream_chat_callback(
            user_query="请总结这篇论文的主要贡献",
            task_type="coolpapaers",
            callback=print_stream,
            cleanup_after_chat=False
        )
    
    # 使用带图像版本
    print("\n\n=== 带图像论文对话示例 ===\n")
    # 创建带图像的PDF处理器
    image_processor = PDFProcessor(converter_type='fitz_with_image', use_cache=True)
    with PaperChat(pdf_processor=image_processor, prompt_type='llm_with_image') as paper_chat:
        # 下载论文
        pdf_path, _ = paper_chat.download_paper_from_arxiv("2303.08774")  # GPT-4论文
        
        # 转换为Markdown，指定图片缓存目录
        paper_chat.convert_paper_to_markdown(
            pdf_path=pdf_path,
            strip_references=True,
            images_cache_dir="./image_cache"  # 使用正确的参数名
        )
        
        # 使用提示词模板
        paper_chat.stream_chat_callback(
            user_query="请用中文总结这篇论文的主要内容和贡献",
            task_type="yuanbao",
            callback=print_stream,
            cleanup_after_chat=False
        )
    
    # 使用便捷函数和图文模式
    print("\n\n=== 使用便捷函数和图文模式 ===\n")
    download_and_chat_with_paper(
        paper_id="2307.09288",  # 任选一篇包含图表的论文
        user_query="请分析这篇论文中的图表内容并解释其含义",
        task_type="coolpapaers",
        stream_callback=print_stream,
        image_text_mode=True,  # 启用图文模式
        pdf_cache_dir="./pdf_cache",  # 使用正确的参数名
        images_cache_dir="./image_cache"  # 使用正确的参数名
    )
    
    # 运行单元测试
    unittest.main()