import sys
import os

# 上一级目录是tests，再上一级目录是SmartPaper
# 这段代码的作用是将当前文件所在目录的上两级目录添加到Python的模块搜索路径中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SmartPaper.file_parsing.pdf_to_md_fitz_with_image import advanced_image_handler, extract_pdf_content

def main() -> None:
    """
    主函数 - 程序入口点
    处理PDF文件并转换为包含图像的Markdown文档
    """
    # 设置输入文件和输出目录
    pdf_file: str = "../test_datas/test.pdf" 
    output_dir: str = "./outputs/test_pdf_to_md_fitz_with_image_output"  

    # 是否去除参考文献部分
    strip_references: bool = True  
    
    # 设置缓存参数
    cache_base64: bool = True
    cache_dir = "./cache"  # 可以设置为具体路径，如 "cache"
    
    # 执行PDF内容提取，使用高级图像处理器
    full_text: str = extract_pdf_content(
        pdf_file,
        output_dir,
        strip_references=strip_references,
        image_handler=advanced_image_handler,  # 使用增强版图像处理器
        api_key=None,  # 如果需要使用图像分析API，请提供密钥
        delete_rendered_images=True,  # 默认删除渲染后的页面图像
        cache_base64=cache_base64,  # 是否缓存base64编码
        cache_dir=cache_dir  # 缓存目录
    )
    print(full_text)  # 打印提取的文本内容
    print("PDF转换完成！")
    


# 程序入口点
if __name__ == "__main__":
    main()
