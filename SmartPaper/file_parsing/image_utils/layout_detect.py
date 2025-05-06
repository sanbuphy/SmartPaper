"""
布局处理模块
负责文档版面分析和处理
"""

import cv2
import json
import os
import time
from typing import Dict, List, Any, Union
from paddlex import create_model

from .layout_config import LayoutConfig

# 全局布局检测模型
LAYOUT_MODEL = None

def init_layout_model(model_name="PP-DocLayout-S"):
    """初始化布局检测模型并返回模型实例"""
    global LAYOUT_MODEL
    if LAYOUT_MODEL is None:
        LAYOUT_MODEL = create_model(model_name=model_name)
    return LAYOUT_MODEL


class LayoutDetector:
    def __init__(
        self,
        model=None,
        enable_label_filtering=True,
        enable_box_containment_analysis=True,
        enable_formula_number_merging=True,
        enable_image_title_merging=True,  
        labels_to_filter=None,
    ):
        """
        初始化布局检测器

        参数:
            model: 使用的模型实例或模型名称，默认使用全局布局检测模型
            enable_label_filtering: 是否启用标签过滤功能
            enable_box_containment_analysis: 是否启用框的包含关系分析
            enable_formula_number_merging: 是否启用公式和公式序号的合并
            enable_image_title_merging: 是否启用图片和图片标题的合并
            labels_to_filter: 要过滤的标签列表，如果为None则使用配置中的过滤设置
        """
        global LAYOUT_MODEL
        # 初始化全局模型（如果尚未初始化）
        if LAYOUT_MODEL is None:
            init_layout_model()
            
        # 判断传入的是模型实例还是模型名称，或使用全局模型
        if model is None:
            self.model = LAYOUT_MODEL
        elif isinstance(model, str):
            self.model = create_model(model_name=model)
        else:
            # 如果是模型实例，直接使用
            self.model = model

        self.config = LayoutConfig()

        # 设置过滤选项
        self.config.enable_filter = enable_label_filtering
        if labels_to_filter is not None:
            self.config.set_filter_labels(labels_to_filter)

        # 添加新的控制属性（私有）
        self._enable_box_containment_analysis = enable_box_containment_analysis
        self._enable_formula_number_merging = enable_formula_number_merging
        self._enable_image_title_merging = enable_image_title_merging  # 新增控制属性

    def detect_layout(
        self,
        image_path: str,
        output_path: str = "./layout_output/layout_detection.json",
        remove_result_file: bool = True,
    ) -> Dict:
        """
        检测文档版面布局

        参数:
            image_path: 图像路径
            output_path: 输出JSON文件路径

        返回:
            版面分析结果
        """
        # 创建输出目录
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        # 设置json输出路径
        json_path = (
            output_path
            if output_path.endswith(".json")
            else os.path.join(output_dir, "layout_detection.json")
        )

        output = self.model.predict(image_path, batch_size=1, layout_nms=True)

        # 保存原始结果到临时JSON文件
        temp_json_path = json_path.replace(".json", "_temp.json")
        for res in output:
            res.save_to_json(save_path=temp_json_path)

        # 读取临时JSON文件
        with open(temp_json_path, "r", encoding="utf-8") as f:
            result = json.load(f)

        # 进行后处理
        processed_result = self.post_process(result)
        
        # 将后处理的结果保存到最终JSON文件
        self._save_result_to_json(processed_result, json_path)
        
        # 删除临时文件
        os.remove(temp_json_path)
        
        # 如果指定要删除结果文件
        if remove_result_file:
            os.remove(json_path)

        return processed_result
        
    def _save_result_to_json(self, result: Dict, json_path: str) -> None:
        """
        将处理后的结果保存为JSON文件，确保复杂结构能够正确序列化
        
        参数:
            result: 要保存的结果
            json_path: 保存路径
        """
        # 处理JSON序列化
        serializable_result = self._make_serializable(result)
        
        # 保存到JSON文件
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(serializable_result, f, ensure_ascii=False, indent=2)
    
    def _make_serializable(self, obj):
        """
        递归地处理对象，使其可JSON序列化
        
        参数:
            obj: 要处理的对象
            
        返回:
            可序列化的对象
        """
        if isinstance(obj, dict):
            # 处理字典
            result = {}
            for key, value in obj.items():
                result[key] = self._make_serializable(value)
            return result
        elif isinstance(obj, list):
            # 处理列表
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            # 处理自定义对象
            return self._make_serializable(obj.__dict__)
        else:
            # 基本类型直接返回
            return obj

    def post_process(self, result: Dict) -> Dict:
        """
        对检测结果进行后处理

        参数:
            result: 原始检测结果

        返回:
            处理后的检测结果
        """
        if not result or not result.get("boxes"):
            return result

        # 过滤掉需要过滤的标签
        if self.config.enable_filter:
            filtered_boxes = []
            for box in result.get("boxes", []):
                label = box.get("label")
                # 判读标签是否需要过滤
                if not self.config.should_filter(label):
                    filtered_boxes.append(box)
            result["boxes"] = filtered_boxes

        # 添加更多的后处理逻辑

        # 1. 构建框的包含关系，移除嵌套框
        if self._enable_box_containment_analysis:
            result["boxes"] = self._organize_boxes_by_containment(result["boxes"])

        # 2. 合并公式和公式序号
        if self._enable_formula_number_merging:
            result["boxes"] = self._merge_formula_with_numbers(result["boxes"])
            
        # 3. 合并图片和图片标题
        if self._enable_image_title_merging:
            result["boxes"] = self._merge_image_with_titles(result["boxes"])

        return result

    def _is_box_contained_in(self, box1: List[float], box2: List[float]) -> bool:
        """
        判断box1是否被box2包含（如果box1有80%以上区域被box2包含，则视为被包含）

        参数:
            box1: [x1, y1, x2, y2] 格式的框坐标
            box2: [x1, y1, x2, y2] 格式的框坐标

        返回:
            bool: 如果box1有80%以上区域被box2包含，返回True，否则返回False
        """
        # 计算box1的面积
        area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])

        # 计算交集的坐标
        intersect_x1 = max(box1[0], box2[0])
        intersect_y1 = max(box1[1], box2[1])
        intersect_x2 = min(box1[2], box2[2])
        intersect_y2 = min(box1[3], box2[3])

        # 如果没有交集，直接返回False
        if intersect_x1 >= intersect_x2 or intersect_y1 >= intersect_y2:
            return False

        # 计算交集的面积
        intersection_area = (intersect_x2 - intersect_x1) * (
            intersect_y2 - intersect_y1
        )

        # 计算交集面积占box1面积的比例
        overlap_ratio = intersection_area / area_box1

        # 如果交集面积占box1面积的比例大于等于0.8，则视为被包含
        return overlap_ratio >= 0.8

    def _organize_boxes_by_containment(self, boxes: List[Dict]) -> List[Dict]:
        """
        为每个框添加包含关系，并移除嵌套在其他框内部的框

        参数:
            boxes: 包含框信息的字典列表，每个字典包含coordinate字段

        返回:
            List[Dict]: 添加了包含关系的框列表
        """
        n = len(boxes)
        is_nested = [False] * n

        # 为每个框添加contains属性
        for i in range(n):
            boxes[i]["contains"] = []

        # 检查每个框是否被其他框包含
        for i in range(n):
            box1 = boxes[i]["coordinate"]
            for j in range(n):
                if i != j:
                    box2 = boxes[j]["coordinate"]
                    if self._is_box_contained_in(box1, box2):
                        is_nested[i] = True
                        # 将被包含的框添加到外部框的contains列表中
                        boxes[j]["contains"].append(boxes[i])
                        break

        # 只保留不是嵌套框的框
        result = []
        for i in range(n):
            if not is_nested[i]:
                result.append(boxes[i])

        return result

    def _calculate_distance_between_boxes(
        self, box1: List[float], box2: List[float]
    ) -> float:
        """
        计算两个框之间的最小边界距离

        参数:
            box1: [x1, y1, x2, y2] 格式的框坐标
            box2: [x1, y1, x2, y2] 格式的框坐标

        返回:
            float: 两个框之间的最小距离，如果重叠则为0
        """
        # 计算水平方向上的距离
        if box1[0] > box2[2]:  # box1在box2右侧
            horizontal_dist = box1[0] - box2[2]
        elif box2[0] > box1[2]:  # box2在box1右侧
            horizontal_dist = box2[0] - box1[2]
        else:  # 水平方向上有重叠
            horizontal_dist = 0

        # 计算垂直方向上的距离
        if box1[1] > box2[3]:  # box1在box2下方
            vertical_dist = box1[1] - box2[3]
        elif box2[1] > box1[3]:  # box2在box1下方
            vertical_dist = box2[1] - box1[3]
        else:  # 垂直方向上有重叠
            vertical_dist = 0

        # 计算欧几里得距离
        return (horizontal_dist**2 + vertical_dist**2) ** 0.5

    def _merge_formula_with_numbers(self, boxes: List[Dict]) -> List[Dict]:
        """
        将公式序号框融合到最近的公式框中，优先考虑序号左侧的公式框

        参数:
            boxes: 包含框信息的字典列表

        返回:
            List[Dict]: 处理后的框列表，原始列表不会被修改
        """
        # 识别所有公式框和公式序号框
        formula_boxes = [box for box in boxes if box.get("label") == "formula"]
        formula_number_boxes = [
            box for box in boxes if box.get("label") == "formula_number"
        ]

        # 如果没有公式序号框或公式框，直接返回原列表的副本
        if not formula_number_boxes or not formula_boxes:
            return boxes.copy()

        # 创建结果列表，首先加入除了公式框和公式序号框外的所有框
        result_boxes = []
        formula_ids = [id(box) for box in formula_boxes]
        formula_number_ids = [id(box) for box in formula_number_boxes]

        # 复制非公式和非公式序号的框到结果列表
        for box in boxes:
            if id(box) not in formula_ids and id(box) not in formula_number_ids:
                result_boxes.append(box.copy())

        # 处理公式框，为每个公式框创建副本
        processed_formula_boxes = []
        for formula_box in formula_boxes:
            new_formula_box = formula_box.copy()
            new_formula_box["formula_numbers"] = []
            processed_formula_boxes.append(new_formula_box)

        # 对于每个公式序号框，找到最合适的公式框并融合
        for number_box in formula_number_boxes:
            number_coord = number_box["coordinate"]

            # 计算公式序号框的左边缘和中心点
            number_left = number_coord[0]
            number_center_y = (number_coord[1] + number_coord[3]) / 2

            # 定义垂直容忍度（公式中心点和序号中心点的垂直距离允许范围）
            vertical_tolerance = (
                number_coord[3] - number_coord[1]
            ) * 2  # 序号高度的2倍

            # 筛选出垂直方向上大致对齐的公式框
            aligned_formulas = []
            for formula_box in processed_formula_boxes:
                formula_coord = formula_box["coordinate"]
                formula_center_y = (formula_coord[1] + formula_coord[3]) / 2

                # 检查垂直方向上是否对齐
                if abs(formula_center_y - number_center_y) <= vertical_tolerance:
                    aligned_formulas.append(formula_box)

            # 先尝试找位于序号左侧的公式框（公式在左，序号在右）
            left_side_formulas = []
            for formula_box in aligned_formulas:
                formula_coord = formula_box["coordinate"]
                formula_right = formula_coord[2]  # 公式框的右边缘

                # 如果公式框的右边缘在序号框的左边缘的左侧或接近（允许少量重叠）
                if (
                    formula_right <= number_left + (number_coord[2] - number_left) * 0.2
                ):  # 允许20%的重叠
                    left_side_formulas.append(formula_box)

            closest_formula = None

            # 如果找到了位于序号左侧的公式框
            if left_side_formulas:
                # 选择最近的一个（公式右边缘离序号左边缘最近的）
                min_distance = float("inf")
                for formula_box in left_side_formulas:
                    formula_right = formula_box["coordinate"][2]

                    distance = number_left - formula_right

                    if distance < min_distance:
                        min_distance = distance
                        closest_formula = formula_box

            # 如果没有找到位于序号左侧的公式框，则在所有垂直对齐的公式框中选择距离最近的
            elif aligned_formulas:
                min_distance = float("inf")
                for formula_box in aligned_formulas:
                    formula_center_x = (formula_box["coordinate"][0] + formula_box["coordinate"][2]) / 2
                    number_center_x = (number_coord[0] + number_coord[2]) / 2

                    distance = abs(formula_center_x - number_center_x)

                    if distance < min_distance:
                        min_distance = distance
                        closest_formula = formula_box

            # 如果仍然没有找到合适的公式框，退回到使用边界距离
            else:
                min_distance = float("inf")
                for formula_box in processed_formula_boxes:
                    distance = self._calculate_distance_between_boxes(
                        formula_box["coordinate"], number_coord
                    )

                    if distance < min_distance:
                        min_distance = distance
                        closest_formula = formula_box

            if closest_formula:
                # 融合公式框和公式序号框
                # 取两个框的并集作为新的公式框
                closest_formula["coordinate"] = [
                    min(closest_formula["coordinate"][0], number_coord[0]),
                    min(closest_formula["coordinate"][1], number_coord[1]),
                    max(closest_formula["coordinate"][2], number_coord[2]),
                    max(closest_formula["coordinate"][3], number_coord[3]),
                ]

                # 添加公式序号的详细信息
                closest_formula["formula_numbers"].append(
                    {
                        "coordinate": number_coord,
                        "score": number_box.get("score", 0),
                        "text": number_box.get("text", ""),
                    }
                )

        # 将处理后的公式框添加到结果列表
        result_boxes.extend(processed_formula_boxes)

        return result_boxes

    def _merge_image_with_titles(self, boxes: List[Dict]) -> List[Dict]:
        """
        将图片标题框添加到相关的图片框中
        
        参数:
            boxes: 包含框信息的字典列表
            
        返回:
            List[Dict]: 处理后的框列表，原始列表不会被修改
        """
        # 识别所有图片框和图表框
        image_boxes = [box for box in boxes if box.get("label") == "image"]
        chart_boxes = [box for box in boxes if box.get("label") == "chart"]
        
        # 识别所有图片标题框和图表标题框
        figure_title_boxes = [box for box in boxes if box.get("label") == "figure_title"]
        chart_title_boxes = [box for box in boxes if box.get("label") == "chart_title"]
        
        # 所有的图片和图表框
        all_image_boxes = image_boxes + chart_boxes
        # 所有的标题框
        all_title_boxes = figure_title_boxes + chart_title_boxes
        
        # 如果没有图片/图表框或标题框，直接返回原列表的副本
        if not all_image_boxes or not all_title_boxes:
            return boxes.copy()
        
        # 创建结果列表
        result_boxes = []
        all_image_ids = [id(box) for box in all_image_boxes]
        all_title_ids = [id(box) for box in all_title_boxes]
        
        # 复制非图片/图表和非标题的框到结果列表
        for box in boxes:
            if id(box) not in all_image_ids and id(box) not in all_title_ids:
                result_boxes.append(box.copy())
        
        # 为所有的图片/图表框创建副本，并初始化contains属性
        processed_image_boxes = []
        for image_box in all_image_boxes:
            new_image_box = image_box.copy()
            if "contains" not in new_image_box:
                new_image_box["contains"] = []
            processed_image_boxes.append(new_image_box)
        
        # 已匹配的标题框ID
        matched_title_ids = set()
        
        # 第一轮：按类型匹配（图片与图片标题，图表与图表标题）
        # 1. 匹配图片和图片标题
        for title_box in figure_title_boxes:
            title_id = id(title_box)
            title_coord = title_box["coordinate"]
            closest_image = None
            min_distance = float("inf")
            
            # 只在图片框中寻找最近的
            for image_box in [box for box in processed_image_boxes if box.get("label") == "image"]:
                image_coord = image_box["coordinate"]
                distance = self._calculate_distance_between_boxes(image_coord, title_coord)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_image = image_box
            
            # 如果找到了匹配的图片框
            if closest_image:
                closest_image["contains"].append(title_box.copy())
                # 扩展图片框以包含标题
                closest_image["coordinate"] = [
                    min(closest_image["coordinate"][0], title_coord[0]),
                    min(closest_image["coordinate"][1], title_coord[1]),
                    max(closest_image["coordinate"][2], title_coord[2]),
                    max(closest_image["coordinate"][3], title_coord[3]),
                ]
                matched_title_ids.add(title_id)
        
        # 2. 匹配图表和图表标题
        for title_box in chart_title_boxes:
            title_id = id(title_box)
            title_coord = title_box["coordinate"]
            closest_chart = None
            min_distance = float("inf")
            
            # 只在图表框中寻找最近的
            for chart_box in [box for box in processed_image_boxes if box.get("label") == "chart"]:
                chart_coord = chart_box["coordinate"]
                distance = self._calculate_distance_between_boxes(chart_coord, title_coord)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_chart = chart_box
            
            # 如果找到了匹配的图表框
            if closest_chart:
                closest_chart["contains"].append(title_box.copy())
                # 扩展图表框以包含标题
                closest_chart["coordinate"] = [
                    min(closest_chart["coordinate"][0], title_coord[0]),
                    min(closest_chart["coordinate"][1], title_coord[1]),
                    max(closest_chart["coordinate"][2], title_coord[2]),
                    max(closest_chart["coordinate"][3], title_coord[3]),
                ]
                matched_title_ids.add(title_id)
        
        # 第二轮：处理未匹配的标题框，尝试找最近的任何图片或图表
        for title_box in all_title_boxes:
            title_id = id(title_box)
            # 如果标题已经匹配，跳过
            if title_id in matched_title_ids:
                continue
                
            title_coord = title_box["coordinate"]
            closest_image = None
            min_distance = float("inf")
            
            # 在所有图片和图表中寻找最近的
            for image_box in processed_image_boxes:
                image_coord = image_box["coordinate"]
                distance = self._calculate_distance_between_boxes(image_coord, title_coord)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_image = image_box
            
            # 如果找到了最近的图片或图表
            if closest_image:
                closest_image["contains"].append(title_box.copy())
                # 扩展图片/图表框以包含标题
                closest_image["coordinate"] = [
                    min(closest_image["coordinate"][0], title_coord[0]),
                    min(closest_image["coordinate"][1], title_coord[1]),
                    max(closest_image["coordinate"][2], title_coord[2]),
                    max(closest_image["coordinate"][3], title_coord[3]),
                ]
        
        # 将处理后的图片和图表框添加到结果列表
        result_boxes.extend(processed_image_boxes)
        
        return result_boxes


# 示例用法
if __name__ == "__main__":
    # 预先初始化全局布局检测模型
    init_layout_model()
    
    image_path = "./image.png"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 使用全局模型创建检测器
    detector = LayoutDetector()
    
    # 测试文档版面分析
    result = detector.detect_layout(
        image_path=image_path,
        output_path=os.path.join(output_dir, "layout_detection.json"),
    )
