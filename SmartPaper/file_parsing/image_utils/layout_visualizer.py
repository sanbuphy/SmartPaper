import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Union, Tuple, Any
from .layout_config import LayoutConfig

class LayoutVisualizer:
    def __init__(self, font_size: int = 12):
        """初始化可视化器
        
        Args:
            font_size: 字体大小，默认12
        """
        # 直接使用simhei字体
        try:
            self.font = ImageFont.truetype("simhei", font_size)
        except:
            print("无法加载simhei字体，使用默认字体")
            self.font = ImageFont.load_default()
        
        # 使用配置文件中的颜色设置
        self.config = LayoutConfig()
        self.default_color = self.config.default_color
    
    def _normalize_coordinate(self, coordinate: Any) -> Tuple[int, int, int, int]:
        """标准化坐标格式
        
        Args:
            coordinate: 坐标，可能的格式有：
                - [x1, y1, x2, y2]
                - [[x1, y1], [x2, y2]]
                - 单个数值 (错误情况)
                
        Returns:
            标准化后的坐标 (x1, y1, x2, y2)
        """
        try:
            if isinstance(coordinate, (int, float)):
                raise ValueError(f"坐标必须是列表或元组，收到: {coordinate}")
                
            if len(coordinate) == 4:
                # 格式: [x1, y1, x2, y2]
                return tuple(map(int, coordinate))
                
            elif len(coordinate) == 2 and isinstance(coordinate[0], (list, tuple)) and len(coordinate[0]) == 2:
                # 格式: [[x1, y1], [x2, y2]]
                return (int(coordinate[0][0]), int(coordinate[0][1]), 
                        int(coordinate[1][0]), int(coordinate[1][1]))
                
            else:
                raise ValueError(f"无法识别的坐标格式: {coordinate}")
                
        except Exception as e:
            print(f"坐标格式错误: {e}, 使用默认值")
            # 返回一个默认的小矩形作为后备方案
            return (0, 0, 10, 10)
        
    def draw_boxes(self, image: np.ndarray, boxes: List[Dict], 
                  show_order: bool = True, show_label: bool = True) -> np.ndarray:
        """绘制排序后的检测框
        
        Args:
            image: 原始图像(RGB格式)
            boxes: 排序后的检测框列表
            show_order: 是否显示排序顺序
            show_label: 是否显示标签类型
            
        Returns:
            绘制了检测框的图像
        """
        # 转换为PIL图像
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        draw = ImageDraw.Draw(pil_image)
        
        # 绘制每个元素
        for i, box in enumerate(boxes):
            # 使用标准化函数处理坐标
            coordinate = box.get('coordinate', [0, 0, 10, 10])
            x1, y1, x2, y2 = self._normalize_coordinate(coordinate)
            
            label = box.get('label', 'unknown')
            score = box.get('score', 0)
            
            # 使用配置文件获取颜色
            color = self.config.get_color(label)
            
            # 绘制矩形框
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            
            # 准备标注文本
            text_elements = []
            if show_order:
                text_elements.append(f"#{i+1}")
            if show_label:
                # 使用配置中的中文标签名(如果有)
                label_display = self.config.get_chinese_name(label) if hasattr(self.config, 'get_chinese_name') else label
                text_elements.append(f"{label_display}")
                if score > 0:
                    text_elements.append(f"{score:.2f}")
            text = " ".join(text_elements)
            
            if text:
                # 获取文本尺寸
                text_bbox = draw.textbbox((0, 0), text, font=self.font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # 绘制文本背景
                draw.rectangle(
                    [x1, y1 - text_height - 8, x1 + text_width + 8, y1],  # 增加内边距
                    fill=color
                )
                
                # 绘制文本
                draw.text(
                    (x1 + 4, y1 - text_height - 4),  # 调整文本位置
                    text,
                    fill=(255, 255, 255),
                    font=self.font
                )
        
        # 转换回OpenCV格式
        result = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return result

    def save_visualization(self, image_path: str, boxes: List[Dict], 
                         output_path: str,
                         show_order: bool = True,
                         show_label: bool = True) -> None:
        """保存可视化结果
        
        Args:
            image_path: 原始图像路径
            boxes: 排序后的检测框列表
            output_path: 输出图像路径
            show_order: 是否显示排序顺序
            show_label: 是否显示标签类型
        """
        # 读取原始图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        # 绘制检测框
        result = self.draw_boxes(image, boxes, show_order, show_label)
        
        # 保存结果
        cv2.imwrite(output_path, result)
        print(f"可视化结果已保存至: {output_path}")


if __name__ == "__main__":
    from layout_detect import LayoutDetector
    import os 
    import json
    image_path = "./image.png"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化检测器
    detector = LayoutDetector()
    
    # 测试文档版面分析
    result = detector.detect_layout(
        image_path=image_path,
        output_path=os.path.join(output_dir, "layout_detection.json"),
    )

    # 读取检测结果
    with open(os.path.join(output_dir, "layout_detection.json"), "r", encoding="utf-8") as f:
        layout_result = json.load(f)
    
    # 初始化可视化器
    visualizer = LayoutVisualizer()
    
    visualizer.save_visualization(
        image_path=image_path,
        boxes=layout_result["boxes"],
        output_path=os.path.join(output_dir, "layout_visualization.jpg"),
        show_order=True,
        show_label=True,
    )
