# image_analysis.py

import os
import base64
import hashlib
import json
from typing import Dict, Any, List, Union, Optional
import logging
from PIL import Image
from openai import OpenAI
import time
from dotenv import load_dotenv
load_dotenv()

# 提示词模板
MULTIMODAL_PROMPT = """
请分析这张图片并生成一个10字以内的标题、50字以内的图片描述，使用JSON格式输出。

分析以下方面:
1. 图像类型（图表、示意图、照片等）
2. 主要内容/主题
3. 包含的关键信息点
4. 图像的可能用途

输出格式必须严格为:
{
  "title": "简洁标题(10字以内)",
  "description": "详细描述(50字以内)",
}

只返回JSON，不要有其他说明文字。
"""


def extract_json_content(text: str) -> Dict[str, Any]:
    """
    从文本中提取JSON内容。

    参数:
        text (str): 可能包含JSON的文本

    返回:
        Dict[str, Any]: 解析后的JSON字典，如果解析失败则返回包含错误信息的字典
    """
    if not text:
        return {"error": "Empty response", "title": "", "description": ""}

    # 尝试寻找JSON的开始和结束位置
    json_start = text.find("{")
    json_end = text.rfind("}")

    if (json_start != -1 and json_end != -1 and json_end > json_start):
        try:
            json_text = text[json_start: json_end + 1]
            result = json.loads(json_text)
            # 确保返回的字典包含必要的键
            if "title" not in result:
                result["title"] = ""
            if "description" not in result:
                result["description"] = ""

            return result
        except json.JSONDecodeError as e:
            return {"error": f"JSON解析失败: {str(e)}", "title": "", "description": ""}

    try:
        result = json.loads(text)
        # 确保返回的字典包含必要的键
        if "title" not in result:
            result["title"] = ""
        if "description" not in result:
            result["description"] = ""
        return result
    except json.JSONDecodeError:
        # 尝试从文本中提取一些信息作为描述
        fallback_description = (
            text.strip().replace("```json", "").replace("```", "").strip()[:50]
        )
        return {
            "error": "无法提取JSON内容",
            "title": "",
            "description": fallback_description,
        }


def image_to_base64(image_path: str) -> str:
    """
    将图像文件转换为base64编码字符串
    
    参数:
        image_path: 图像文件路径
        
    返回:
        base64编码的图像字符串
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string
    except FileNotFoundError:
        raise FileNotFoundError(f"文件未找到: {image_path}")


class ImageAnalysis:
    """
    图像文本提取器类，用于将图像内容转换为文本描述和标题。

    该类使用OpenAI的多模态模型分析图像内容，生成描述性文本和标题。
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.siliconflow.cn/v1",
        vision_model: str = None,
        availabale_vision_models: List[str] = [
            "Qwen/Qwen2.5-VL-32B-Instruct",
            "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
        ],  
        prompt: Optional[str] = None,
    ):
        # 优先使用传入的API密钥，否则从环境变量中读取
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # 确保有可用的API密钥
        if not self.api_key:
            raise ValueError("API密钥未提供，请设置OPENAI_API_KEY环境变量或传入api_key参数。")

        else:
            # 设置基础URL，优先使用传入的，否则从环境变量读取
            self.base_url = base_url or os.getenv("OPENAI_API_BASE")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        # 设置默认视觉模型
        self.vision_model = vision_model or availabale_vision_models[0]

        # 设置提示词
        self._prompt = prompt or MULTIMODAL_PROMPT

    def analyze_image(
        self,
        image_url: str = None,
        local_image_path: str = None,
        model: str = None,
        detail: str = "low",
        prompt: str = None,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """
        分析图像并返回描述信息。

        Args:
            image_url: 在线图片URL
            local_image_path: 本地图片路径
            model: 使用的视觉模型，默认使用实例的默认模型
            detail: 图像细节级别，'low'或'high'
            prompt: 自定义提示词
            temperature: 模型温度参数

        Returns:
            包含title和description的字典
        """
        # 基本参数检查
        if not image_url and not local_image_path:
            raise ValueError("必须提供一个图像来源：image_url或local_image_path")
        if image_url and local_image_path:
            raise ValueError("只能提供一个图像来源：image_url或local_image_path")

        # 处理图像来源
        final_image_url = image_url
        image_format = "jpeg" # 默认格式
        if local_image_path:
            # 简化图片格式处理
            try:
                with Image.open(local_image_path) as img:
                    image_format = img.format.lower() if img.format else "jpeg"
            except Exception as e:
                 logging.warning(f"无法打开或识别图片格式 {local_image_path}: {e}, 使用默认jpeg")

            base64_image = image_to_base64(local_image_path)
            final_image_url = f"data:image/{image_format};base64,{base64_image}"

        model_to_use = model or self.vision_model
        prompt_text = prompt or self._prompt

        try:
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": final_image_url, "detail": detail},
                            },
                            {"type": "text", "text": prompt_text},
                        ],
                    }
                ],
                temperature=temperature,
                max_tokens=300,
            )

            # 解析结果
            result_content = response.choices[0].message.content
            analysis_result = extract_json_content(result_content)
            
            return analysis_result

        except Exception as e:
            # 错误处理
            print(f"API调用失败: {e}")
            return {"error": f"API调用失败: {str(e)}", "title": "", "description": ""}


if __name__ == "__main__":
    image_analyzer = ImageAnalysis()
    
    local_image = "./image.png"
    
    # 分析图像
    start_time = time.time()
    result = image_analyzer.analyze_image(
        local_image_path=local_image,
        model="Qwen/Qwen2.5-VL-32B-Instruct",
        detail="low",
        prompt=MULTIMODAL_PROMPT,
        temperature=0.1,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"耗时: {time.time() - start_time:.2f}秒")

