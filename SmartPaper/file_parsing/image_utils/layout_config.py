"""
LayoutConfig类定义了文档布局的标签和颜色配置
以及过滤标签的功能。
"""
from typing import Dict, List, Tuple, Optional, Any


class LayoutConfig:
    def __init__(self):
        self.enable_filter = True
        self.filter_labels = None  # 如果设置了，则只过滤这个列表中的标签
        
        self.default_color = (128, 128, 128)  # 灰色，用于未定义颜色的标签

        # 标签管理 - 所有信息集中在一起
        self.labels = {
            'paragraph_title': {
                'id': 0,
                'chinese_name': '段落标题',
                'filter': False,     # 是否需要过滤
                'color': (255, 0, 0) # 红色
            },
            'image': {
                'id': 1,
                'chinese_name': '图片',
                'filter': False,
                'color': (0, 0, 255) # 蓝色
            },
            'text': {
                'id': 2,
                'chinese_name': '正文文本',
                'filter': False,
                'color': (0, 255, 0) # 绿色
            },
            'number': {
                'id': 3,
                'chinese_name': '数字', # 一般是页码
                'filter': True,
                'color': (218, 165, 32) # 金麦色
            },
            'abstract': {
                'id': 4,
                'chinese_name': '摘要',
                'filter': False,
                'color': (0, 255, 191) # 绿松石色
            },
            'content': {
                'id': 5,
                'chinese_name': '目录',
                'filter': False,
                'color': self.default_color
            },
            'figure_title': {
                'id': 6,
                'chinese_name': '图表标题',
                'filter': False,
                'color': (128, 0, 255) # 紫色
            },
            'formula': {
                'id': 7,
                'chinese_name': '公式',
                'filter': False,
                'color': (255, 255, 0) # 黄色
            },
            'table': {
                'id': 8,
                'chinese_name': '表格',
                'filter': False,
                'color': (255, 165, 0) # 橙色
            },
            'table_title': {
                'id': 9,
                'chinese_name': '表格标题',
                'filter': False,
                'color': (255, 140, 0) # 深橙色
            },
            'reference': {
                'id': 10,
                'chinese_name': '引用/参考文献',
                'filter': True,
                'color': self.default_color
            },
            'doc_title': {
                'id': 11,
                'chinese_name': '文档标题',
                'filter': False,
                'color': (255, 0, 128) # 品红色
            },
            'footnote': {
                'id': 12,
                'chinese_name': '脚注',
                'filter': True,
                'color': (144, 238, 144) # 淡绿色
            },
            'header': {
                'id': 13,
                'chinese_name': '页眉',
                'filter': True,
                'color': (169, 169, 169) # 深灰色
            },
            'algorithm': {
                'id': 14,
                'chinese_name': '算法',
                'filter': False,
                'color': self.default_color
            },
            'footer': {
                'id': 15,
                'chinese_name': '页脚',
                'filter': True,
                'color': (192, 192, 192) # 浅灰色
            },
            'seal': {
                'id': 16,
                'chinese_name': '印章',
                'filter': True,
                'color': self.default_color
            },
            'chart_title': {
                'id': 17,
                'chinese_name': '图表标题',
                'filter': False,
                'color': (0, 215, 255) # 浅青色
            },
            'chart': {
                'id': 18,
                'chinese_name': '图表',
                'filter': False,
                'color': (0, 255, 255) # 青色
            },
            'formula_number': {
                'id': 19,
                'chinese_name': '公式编号',
                'filter': False,
                'color': (255, 215, 0) # 金色
            },
            'header_image': {
                'id': 20,
                'chinese_name': '页眉图片',
                'filter': True,
                'color': self.default_color
            },
            'footer_image': {
                'id': 21,
                'chinese_name': '页脚图片',
                'filter': True,
                'color': self.default_color
            },
            'aside_text': {
                'id': 22,
                'chinese_name': '侧边文本',
                'filter': True,
                'color': (152, 251, 152) # 浅绿色
            }
        }
    
    def get_color(self, label: str) -> Tuple[int, int, int]:
        """获取标签对应的颜色"""
        if label in self.labels:
            return self.labels[label]['color']
        return self.default_color
    
    def get_label_name(self, label_id: int) -> Optional[str]:
        """通过ID获取标签名称"""
        for label, info in self.labels.items():
            if info['id'] == label_id:
                return label
        return None
    
    def get_chinese_name(self, label: str) -> str:
        """获取标签的中文名称"""
        if label in self.labels:
            return self.labels[label]['chinese_name']
        return label
    
    def should_filter(self, label: str) -> bool:
        """判断标签是否需要过滤"""
        if not self.enable_filter:
            return False
        
        # 如果指定了过滤标签列表，则只过滤列表中的标签
        if self.filter_labels is not None:
            return label in self.filter_labels
            
        # 否则使用标签的默认过滤设置
        if label in self.labels:
            return self.labels[label]['filter']
            
        return False
    
    def set_filter_labels(self, filter_labels: List[str]) -> None:
        """设置要过滤的标签列表"""
        self.filter_labels = filter_labels
    
    def filter_labels_list(self, labels: List[str]) -> List[str]:
        """
        过滤输入的标签列表
        
        参数:
            labels: 要过滤的标签列表
            
        返回:
            过滤后的标签列表
        """
        if not labels or not self.enable_filter:
            return labels
            
        return [label for label in labels if not self.should_filter(label)]


