#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SmartPaper测试运行脚本

此脚本用于自动运行SmartPaper项目的测试。
可以运行所有测试或指定特定的测试。

使用方法:
    - 运行所有测试: python run_tests.py
    - 运行特定类别测试: python run_tests.py --category core
    - 运行特定测试文件: python run_tests.py --file test_paper_url.py
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def get_test_files(base_dir, category=None, file_name=None):
    """
    获取要运行的测试文件列表

    Args:
        base_dir: 测试基础目录
        category: 测试类别（core, tools, integration, utils）
        file_name: 指定的测试文件名

    Returns:
        list: 测试文件路径列表
    """
    test_files = []

    if file_name:
        # 如果指定了具体文件，则在所有测试目录中查找该文件
        for root, _, files in os.walk(base_dir):
            if file_name in files:
                test_files.append(os.path.join(root, file_name))
    elif category:
        # 如果指定了类别，则运行该类别下的所有测试
        category_dir = os.path.join(base_dir, category)
        if os.path.exists(category_dir):
            test_files.append(category_dir)
    else:
        # 如果没有指定，运行所有测试
        test_files.append(base_dir)

    return test_files


def run_tests(test_paths, verbose=False):
    """
    运行给定路径的测试

    Args:
        test_paths: 测试文件或目录路径列表
        verbose: 是否显示详细输出

    Returns:
        bool: 测试是否全部通过
    """
    if not test_paths:
        print("未找到符合条件的测试文件")
        return False

    all_passed = True
    for path in test_paths:
        print(f"\n运行测试: {path}")

        cmd = ["python", "-m", "pytest", path]
        if verbose:
            cmd.append("-v")

        result = subprocess.run(cmd)

        if result.returncode != 0:
            all_passed = False

    return all_passed


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="SmartPaper测试运行工具")

    parser.add_argument(
        "--category",
        choices=["core", "tools", "integration", "utils"],
        help="要运行的测试类别（core, tools, integration, utils）",
    )
    parser.add_argument("--file", help="要运行的特定测试文件名（例如：test_paper_url.py）")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")

    args = parser.parse_args()

    # 确定测试基础目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 获取测试文件列表
    test_paths = get_test_files(current_dir, args.category, args.file)

    # 运行测试
    success = run_tests(test_paths, args.verbose)

    # 设置退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
