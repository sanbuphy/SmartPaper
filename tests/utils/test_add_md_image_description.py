"""
测试 add_md_image_description 函数给markdown文件内的图片添加注释，主要判断依据是是否报错。
"""

import sys
import os
import pytest


from utils.add_md_image_description import add_md_image_description


def test_add_image_description():
    current_file_dir = os.path.abspath(os.path.dirname(__file__))
    abs_file_path = os.path.join(
        current_file_dir,
        "test_datas/test_mineru_outputs/test_mineru_add_image_description_如何阅读一本书.md",
    )
    try:
        add_md_image_description(abs_file_path, force_add_desc=True)
    except Exception:
        pytest.fail("add_md_image_description raised an exception")
