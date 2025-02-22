"download_and_modify_json代码从官方复制而来……主要用来下载mineru使用的模型文件。"

from src.tools.download_models import download_and_modify_json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if __name__ == "__main__":
    download_and_modify_json()
