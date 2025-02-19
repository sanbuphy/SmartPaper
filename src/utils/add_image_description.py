import os
import re
from pathlib import Path

def read_markdown_files(path):
    """读取指定路径下的所有Markdown文件"""
    path = Path(path)
    if path.is_file() and path.suffix.lower() in ('.md', '.markdown'):
        return [str(path)]
    return [str(p) for p in path.rglob('*') if p.suffix.lower() in ('.md', '.markdown')]

def process_markdown_file(file_path, force_add_desc=False):
    """处理单个Markdown文件，为无描述的图片添加AI生成的描述"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        markdown_dir = os.path.dirname(file_path)
        modified = False

        # 使用闭包保持状态
        def desc_replacer(match):
            nonlocal modified
            desc, img_path = match.groups()
            if force_add_desc or not desc.strip():
                full_path = os.path.normpath(os.path.join(markdown_dir, img_path))
                if os.path.exists(full_path):
                    new_desc = VLM_description(full_path)
                    modified = True
                    return f'![{new_desc}]({img_path})'
            return match.group(0)

        pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
        new_content = pattern.sub(desc_replacer, content)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"已更新文件: {file_path}")
        else:
            print(f"无需修改: {file_path}")

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")

def VLM_description(image_path):
    """多模态模型生成描述（示例实现）"""
    # TODO: 替换为实际的模型调用
    return f"图片描述 - {os.path.basename(image_path)}"

def main(directory):
    """主处理流程"""
    for md_file in read_markdown_files(directory):
        print(f"正在处理: {md_file}")
        process_markdown_file(md_file, force_add_desc=True)

if __name__ == "__main__":
    target = "output/如何阅读一本书-output-9d95fe4c-a57b-55c1-bdbb-ccd092ba3566/如何阅读一本书-output.md"
    main(target)
