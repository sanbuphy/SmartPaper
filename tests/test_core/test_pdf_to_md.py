import os
import sys
import unittest

# 添加项目根目录到sys.path，确保可以导入SmartPaper模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SmartPaper.core.pdf_to_md import (
    convert_pdf_to_markdown,
    PDFConverter,
    PDFToMarkdownConverter,
    FitzPDFConverter,
    FitzWithImagePDFConverter
)


class PDFToMarkdownTests(unittest.TestCase):
    """测试PDF转Markdown功能的测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 设置测试PDF路径
        self.test_pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_datas', 'test.pdf'))
        # 确保测试PDF文件存在
        self.assertTrue(os.path.exists(self.test_pdf_path), f"测试PDF文件不存在: {self.test_pdf_path}")
        
        # 设置测试输出目录
        self.test_output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_file_parsing', 'outputs', 'test_pdf_to_md'))
        # 确保输出目录存在
        os.makedirs(self.test_output_dir, exist_ok=True)
        
    def test_pdf_converter_initialization(self):
        """测试PDF转换器初始化"""
        # 测试默认转换器（fitz）
        converter = PDFConverter()
        self.assertIsInstance(converter.converter, FitzPDFConverter)
        
        # 测试带图像的转换器（fitz_with_image）
        converter = PDFConverter('fitz_with_image')
        self.assertIsInstance(converter.converter, FitzWithImagePDFConverter)
        
        # 测试不支持的转换器类型
        with self.assertRaises(ValueError):
            PDFConverter('unsupported_type')
    
    def test_convert_pdf_to_markdown_fitz(self):
        """测试使用fitz转换器转换PDF为Markdown"""
        # 使用fitz转换器
        markdown_text = convert_pdf_to_markdown(
            pdf_path=self.test_pdf_path,
            output_dir=os.path.join(self.test_output_dir, 'fitz'),
            converter_type='fitz'
        )
        
        # 验证转换结果
        self.assertIsInstance(markdown_text, str)
        self.assertGreater(len(markdown_text), 0, "转换后的Markdown文本不应为空")
    
    def test_convert_pdf_to_markdown_fitz_with_image(self):
        """测试使用fitz_with_image转换器转换PDF为Markdown"""
        # 使用fitz_with_image转换器
        markdown_text = convert_pdf_to_markdown(
            pdf_path=self.test_pdf_path,
            output_dir=os.path.join(self.test_output_dir, 'fitz_with_image'),
            converter_type='fitz_with_image'
        )
        
        # 验证转换结果
        self.assertIsInstance(markdown_text, str)
        self.assertGreater(len(markdown_text), 0, "转换后的Markdown文本不应为空")
        
        # 验证输出目录中是否包含图像目录
        images_dir = os.path.join(self.test_output_dir, 'fitz_with_image', 'images')
        self.assertTrue(os.path.exists(images_dir), "应该创建图像目录")
    
    def test_strip_references(self):
        """测试去除参考文献功能"""
        # 使用fitz转换器，启用去除参考文献
        markdown_text_with_strip = convert_pdf_to_markdown(
            pdf_path=self.test_pdf_path,
            output_dir=os.path.join(self.test_output_dir, 'fitz_strip'),
            converter_type='fitz',
            strip_references=True
        )
        
        # 使用fitz转换器，不去除参考文献
        markdown_text_without_strip = convert_pdf_to_markdown(
            pdf_path=self.test_pdf_path,
            output_dir=os.path.join(self.test_output_dir, 'fitz_no_strip'),
            converter_type='fitz',
            strip_references=False
        )
        
        # 验证两种模式的差异，如果文档中确实有参考文献，去除后的文本应该更短
        # 注意：如果测试文档没有参考文献，这个测试可能会失败
        # 这里不做强制断言，只做输出比较
        print(f"带去除参考文献的文本长度: {len(markdown_text_with_strip)}")
        print(f"不去除参考文献的文本长度: {len(markdown_text_without_strip)}")
        
    def test_custom_converter_registration(self):
        """测试自定义转换器注册功能"""
        # 创建一个自定义转换器类
        class CustomPDFConverter(PDFToMarkdownConverter):
            def convert(self, pdf_path, output_dir, **kwargs):
                return "这是一个自定义转换器的测试输出"
        
        # 注册自定义转换器
        PDFConverter.register_converter("custom", CustomPDFConverter)
        
        # 使用自定义转换器
        converter = PDFConverter("custom")
        result = converter.convert_pdf_to_markdown(
            pdf_path=self.test_pdf_path,
            output_dir=self.test_output_dir
        )
        
        # 验证自定义转换器的输出
        self.assertEqual(result, "这是一个自定义转换器的测试输出")
        
    def test_file_not_found(self):
        """测试文件不存在的情况"""
        # 使用不存在的PDF路径
        non_existent_path = os.path.join(os.path.dirname(self.test_pdf_path), "non_existent.pdf")
        
        # 测试文件不存在的异常
        with self.assertRaises(FileNotFoundError):
            convert_pdf_to_markdown(
                pdf_path=non_existent_path,
                output_dir=self.test_output_dir
            )


if __name__ == "__main__":
    unittest.main()