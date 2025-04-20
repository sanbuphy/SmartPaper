#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SmartPaper - Streamlit应用启动脚本

此脚本用于通过pip安装后启动Streamlit Web界面
"""

import os
import sys
import subprocess


def main():
    """启动Streamlit应用"""
    streamlit_app = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streamlit.app.py")
    subprocess.run(["streamlit", "run", streamlit_app])


if __name__ == "__main__":
    main()
