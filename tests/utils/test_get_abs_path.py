"""
此函数主要是测试将相对路径转绝对路径
"""

import sys
import pytest
import os


from utils.get_abs_path import get_abs_path

# 创建测试数据目录和文件
test_data_dir = os.path.join(os.path.dirname(__file__), "test_get_abs_path_datas")
os.makedirs(test_data_dir, exist_ok=True)

test_file_1 = os.path.join(test_data_dir, "test_file_1.txt")
test_file_2 = os.path.join(test_data_dir, "test_file_2.txt")

with open(test_file_1, "w") as f:
    f.write("This is a test file.")

with open(test_file_2, "w") as f:
    f.write("This is another test file.")


def test_get_abs_path_with_absolute_path():
    abs_path = os.path.abspath(test_file_1)
    assert get_abs_path(abs_path) == abs_path


def test_get_abs_path_with_relative_path():
    rel_path = os.path.relpath(test_file_1)
    abs_path = os.path.abspath(test_file_1)
    assert get_abs_path(rel_path) == abs_path


def test_get_abs_path_with_base_dir():
    base_dir = test_data_dir
    file_name = os.path.basename(test_file_1)
    abs_path = os.path.abspath(test_file_1)
    assert get_abs_path(file_name, base_dir) == abs_path


def test_get_abs_path_file_not_exist():
    with pytest.raises(ValueError, match="文件不存在"):
        get_abs_path("non_existent_file.txt")


def test_get_abs_path_invalid_base_dir():
    with pytest.raises(ValueError, match="基础目录不存在"):
        get_abs_path("some_file.txt", base_dir="/invalid/base/dir")
