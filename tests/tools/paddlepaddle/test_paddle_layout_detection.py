"""
测试paddlex库构建的paddle_layout_detection.py文件
"""

import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)

from tools.paddlepaddle.paddle_layout_detection import detect_layout

if __name__ == "__main__":
    image_path = "test_paddlepaddle_datas/image.png"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    detect_layout(
        image_path=image_path,
        save_path=os.path.join(current_dir, "test_paddle_layout_detection_output/result.png"),
        json_path=os.path.join(current_dir, "test_paddle_layout_detection_output/res.json"),
    )
