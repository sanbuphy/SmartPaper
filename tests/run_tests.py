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
    - 包含magic_pdf相关测试: python run_tests.py --include-magic-pdf
    - 排除集成测试: python run_tests.py --exclude-integration
"""

import os
import sys
import argparse
import subprocess
import re
from pathlib import Path
from loguru import logger


def check_is_magic_pdf_test(file_path):
    """
    检查文件是否为 magic_pdf 相关测试

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否为 magic_pdf 相关测试
    """
    magic_pdf_tests = ["test_pdf_to_md_mineru.py"]
    return os.path.basename(file_path) in magic_pdf_tests


def get_test_files(
    base_dir,
    category=None,
    file_name=None,
    include_magic_pdf=False,
    run_integration=False,
    exclude_integration=True,
):
    """
    获取要运行的测试文件列表

    Args:
        base_dir: 测试基础目录
        category: 测试类别（core, tools, integration, utils）
        file_name: 指定的测试文件名
        include_magic_pdf: 是否包含 magic_pdf 相关测试
        run_integration: 是否运行集成测试
        exclude_integration: 是否排除集成测试

    Returns:
        list: 测试文件路径列表
    """
    test_files = []

    if file_name:
        # 如果指定了具体文件，则在所有测试目录中查找该文件
        for root, _, files in os.walk(base_dir):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                # 如果不包含 magic_pdf 测试且该文件是 magic_pdf 测试，则跳过
                if not include_magic_pdf and check_is_magic_pdf_test(file_path):
                    continue
                # 如果排除集成测试且该文件在集成测试目录中，则跳过
                if exclude_integration and "integration" in file_path:
                    continue
                test_files.append(file_path)
    elif category:
        # 如果指定了类别，则运行该类别下的所有测试
        category_dir = os.path.join(base_dir, category)
        if os.path.exists(category_dir):
            if include_magic_pdf:
                test_files.append(category_dir)
            else:
                # 遍历目录，逐个添加非 magic_pdf 的测试文件
                for root, _, files in os.walk(category_dir):
                    for file in files:
                        if file.startswith("test_") and file.endswith(".py"):
                            file_path = os.path.join(root, file)
                            if not check_is_magic_pdf_test(file_path):
                                # 如果排除集成测试且该文件在集成测试目录中，则跳过
                                if exclude_integration and "integration" in file_path:
                                    continue
                                test_files.append(file_path)
    else:
        # 如果没有指定，运行所有测试
        if include_magic_pdf:
            if exclude_integration:
                # 排除集成测试目录
                for root, dirs, _ in os.walk(base_dir):
                    if "integration" in dirs:
                        dirs.remove("integration")
                    test_files.append(root)
            else:
                test_files.append(base_dir)
        else:
            # 遍历所有测试目录，逐个添加非 magic_pdf 的测试文件
            for root, _, files in os.walk(base_dir):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        if not check_is_magic_pdf_test(file_path):
                            # 如果排除集成测试且该文件在集成测试目录中，则跳过
                            if exclude_integration and "integration" in file_path:
                                continue
                            test_files.append(file_path)

    # 如果需要运行集成测试
    if run_integration:
        integration_dir = os.path.join(base_dir, "integration")
        if os.path.exists(integration_dir):
            for root, _, files in os.walk(integration_dir):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        if not check_is_magic_pdf_test(file_path) or include_magic_pdf:
                            test_files.append(file_path)

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
        logger.info("未找到符合条件的测试文件")
        return False

    all_passed = True
    for path in test_paths:
        logger.info(f"\n运行测试: {path}")

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
    parser.add_argument(
        "--include-magic-pdf", action="store_true", help="包含 magic_pdf 相关测试（默认忽略）"
    )
    parser.add_argument("--run-integration", action="store_true", help="运行集成测试")
    parser.add_argument(
        "--exclude-integration", action="store_true", default=True, help="排除集成测试（默认启用）"
    )

    args = parser.parse_args()

    # 如果明确要运行集成测试，则不排除集成测试
    if args.run_integration:
        args.exclude_integration = False

    # 确定测试基础目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 获取测试文件列表
    test_paths = get_test_files(
        current_dir,
        args.category,
        args.file,
        args.include_magic_pdf,
        args.run_integration,
        args.exclude_integration,
    )

    # 运行测试
    success = run_tests(test_paths, args.verbose)

    # 设置退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
