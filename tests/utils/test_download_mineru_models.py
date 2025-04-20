"""
测试 mineru 模型下载功能。
主要测试:
1. 模型文件的下载
2. 配置文件的生成和修改
"""

import os
import sys
import pytest


from tools.everything_to_text.pdf_to_md_mineru import download_and_setup_models


def test_download_and_setup_models():
    """测试模型下载和配置功能"""
    try:
        # 执行模型下载和配置
        download_and_setup_models()

        # 检查配置文件是否生成
        home_dir = os.path.expanduser("~")
        config_file = os.path.join(home_dir, "magic-pdf.json")
        assert os.path.exists(config_file), f"配置文件未找到: {config_file}"

    except Exception as e:
        pytest.fail(f"模型下载或配置过程中出现错误: {e}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
