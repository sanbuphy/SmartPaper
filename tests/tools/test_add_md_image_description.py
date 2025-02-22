"""
测试 add_md_image_description 函数给markdown文件内的图片添加注释，主要判断依据是是否报错。
"""

import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.add_md_image_description import add_md_image_description


def test_add_image_description():
    abs_file_path = os.path.abspath(
        "test_datas/outputs/如何阅读一本书-output-9f96686d-a662-474c-a04c-408c374231a5/如何阅读一本书-output.md"
    )
    try:
        add_md_image_description(abs_file_path, force_add_desc=True)
    except Exception:
        pytest.fail("add_md_image_description raised an exception")
