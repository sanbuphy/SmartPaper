import sys
import  os

from src.utils.vlm_function import describe_image, save_result_to_file, extract_text_from_image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


if __name__ == "__main__":
    image_path: str = "page_1.png"

    # 获取图像描述
    description: str = describe_image(image_path,description_prompt_path="description_prompt.md")
    save_result_to_file(description, 'description.md')

    # 从图像中提取文本
    extracted_text: str = extract_text_from_image(image_path,ocr_prompt_path="ocr_prompt.md")
    save_result_to_file(extracted_text, 'extracted_text.md')