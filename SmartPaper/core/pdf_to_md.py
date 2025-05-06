"""
pdf转markdown的转换器实现
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

from SmartPaper.file_parsing.pdf_to_md_fitz import extract_pdf_content as fitz_extract
from SmartPaper.file_parsing.pdf_to_md_fitz_with_image import extract_pdf_content as fitz_with_image_extract


class PDFToMarkdownConverter(ABC):
    """
    PDF转Markdown的抽象基类
    
    所有PDF转换器都应该继承此类并实现convert方法
    """
    
    @abstractmethod
    def convert(self, pdf_path: str, output_dir: str, **kwargs) -> str:
        """
        将PDF转换为Markdown文本
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            **kwargs: 额外参数
            
        Returns:
            str: 转换后的Markdown文本
        """
        pass


class FitzPDFConverter(PDFToMarkdownConverter):
    """
    基于PyMuPDF(fitz)的基础PDF转换器
    
    只提取文本内容，不处理图片
    """
    
    def convert(self, pdf_path: str, output_dir: str, **kwargs) -> str:
        """
        使用fitz提取PDF文本
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            **kwargs: 额外参数，包括:
                - strip_references: 是否去除参考文献部分，默认为False
                
        Returns:
            str: 转换后的Markdown文本
        """
        strip_references = kwargs.get('strip_references', False)
        
        return fitz_extract(
            pdf_path=pdf_path,
            output_dir=output_dir,
            strip_references=strip_references
        )


class FitzWithImagePDFConverter(PDFToMarkdownConverter):
    """
    基于PyMuPDF(fitz)的增强PDF转换器
    
    提取文本内容并处理图片
    """
    
    def convert(self, pdf_path: str, output_dir: str, **kwargs) -> str:
        """
        使用fitz_with_image提取PDF文本和图片
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            **kwargs: 额外参数，包括:
                - strip_references: 是否去除参考文献部分，默认为False
                - api_key: 图像分析API密钥
                - delete_rendered_images: 是否删除渲染后的页面图像，默认为True
                - cache_base64: 是否缓存图像的base64编码，默认为True
                - cache_dir: 图片缓存目录路径 (注意：这是存储图片的缓存目录)
                
        Returns:
            str: 转换后的Markdown文本
        """
        strip_references = kwargs.get('strip_references', False)
        api_key = kwargs.get('api_key', None)
        delete_rendered_images = kwargs.get('delete_rendered_images', True)
        cache_base64 = kwargs.get('cache_base64', True)
        cache_dir = kwargs.get('cache_dir', None)
        
        # 使用高级图像处理函数
        from SmartPaper.file_parsing.pdf_to_md_fitz_with_image import advanced_image_handler
        
        return fitz_with_image_extract(
            pdf_path=pdf_path,
            output_dir=output_dir,
            strip_references=strip_references,
            image_handler=advanced_image_handler,
            api_key=api_key,
            delete_rendered_images=delete_rendered_images,
            cache_base64=cache_base64,
            cache_dir=cache_dir
        )


class PDFConverter:
    """
    PDF转换器工厂类
    
    用于选择和使用不同的PDF转换器实现
    """
    
    # 可用的转换器类型
    CONVERTER_TYPES = {
        'fitz': FitzPDFConverter,
        'fitz_with_image': FitzWithImagePDFConverter
    }
    
    def __init__(self, converter_type: str = 'fitz'):
        """
        初始化PDF转换器
        
        Args:
            converter_type: 转换器类型，可选值: 'fitz'(默认), 'fitz_with_image'
        """
        if converter_type not in self.CONVERTER_TYPES:
            raise ValueError(f"不支持的转换器类型: {converter_type}。可用类型: {', '.join(self.CONVERTER_TYPES.keys())}")
        
        self.converter = self.CONVERTER_TYPES[converter_type]()
    
    def convert_pdf_to_markdown(self, pdf_path: str, output_dir: str, **kwargs) -> str:
        """
        将PDF转换为Markdown文本
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            **kwargs: 额外参数，根据不同转换器有所不同
            
        Returns:
            str: 转换后的Markdown文本
        """
        # 检查文件和目录是否存在
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 使用选择的转换器进行转换
        return self.converter.convert(pdf_path, output_dir, **kwargs)
    
    @classmethod
    def register_converter(cls, name: str, converter_class: type) -> None:
        """
        注册新的转换器类型
        
        Args:
            name: 转换器名称
            converter_class: 转换器类，必须继承PDFToMarkdownConverter
        """
        if not issubclass(converter_class, PDFToMarkdownConverter):
            raise TypeError(f"转换器类必须继承PDFToMarkdownConverter，但获得了: {converter_class.__name__}")
        
        cls.CONVERTER_TYPES[name] = converter_class
        print(f"成功注册转换器: {name}")


def convert_pdf_to_markdown(
    pdf_path: str,
    output_dir: str,
    converter_type: str = 'fitz',
    strip_references: bool = False,
    api_key: Optional[str] = None,
    delete_rendered_images: bool = True,
    cache_base64: bool = True,
    cache_dir: Optional[str] = None
) -> str:
    """
    便捷函数：将PDF转换为Markdown文本
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录，用于存储临时处理文件
        converter_type: 转换器类型，可选值: 'fitz'(默认), 'fitz_with_image'
        strip_references: 是否去除参考文献部分，默认为False
        api_key: 图像分析API密钥，仅在使用fitz_with_image转换器时有效
        delete_rendered_images: 是否删除渲染后的页面图像，默认为True
        cache_base64: 是否缓存图像的base64编码，默认为True
        cache_dir: 图片缓存目录路径，仅在使用fitz_with_image转换器时有效。
                  注意：这是存储图片的缓存目录，不是PDF解析结果的缓存目录。
        
    Returns:
        str: 转换后的Markdown文本
    """
    converter = PDFConverter(converter_type)
    
    kwargs = {
        'strip_references': strip_references
    }
    
    # 如果使用带图像的转换器，添加相关参数
    if converter_type == 'fitz_with_image':
        kwargs.update({
            'api_key': api_key,
            'delete_rendered_images': delete_rendered_images,
            'cache_base64': cache_base64,
            'cache_dir': cache_dir  # 图片缓存目录
        })
    
    return converter.convert_pdf_to_markdown(pdf_path, output_dir, **kwargs)


if __name__ == "__main__":
    # 示例用法
    pdf_path = "test.pdf"
    output_dir = "outputs"
    
    # 基础转换器
    markdown_basic = convert_pdf_to_markdown(
        pdf_path=pdf_path,
        output_dir=output_dir,
        converter_type='fitz',
        strip_references=True
    )
    print(f"基础转换器提取了 {len(markdown_basic)} 字符")
    
    # 带图像的转换器
    markdown_with_images = convert_pdf_to_markdown(
        pdf_path=pdf_path,
        output_dir=output_dir + "_with_images",
        converter_type='fitz_with_image',
        strip_references=True
    )
    print(f"带图像的转换器提取了 {len(markdown_with_images)} 字符")