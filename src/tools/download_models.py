"""
来自官方的代码
"""

import json
import os

import requests
from modelscope import snapshot_download


def download_json(url):
    # 下载JSON文件
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    return response.json()


def download_and_modify_json():
    mineru_patterns = [
        "models/Layout/LayoutLMv3/*",
        "models/Layout/YOLO/*",
        "models/MFD/YOLO/*",
        "models/MFR/unimernet_small_2501/*",
        "models/TabRec/TableMaster/*",
        "models/TabRec/StructEqTable/*",
    ]
    model_dir = snapshot_download("opendatalab/PDF-Extract-Kit-1.0", allow_patterns=mineru_patterns)
    layoutreader_model_dir = snapshot_download("ppaanngggg/layoutreader")
    model_dir = model_dir + "/models"
    print(f"model_dir is: {model_dir}")
    print(f"layoutreader_model_dir is: {layoutreader_model_dir}")

    json_url = "https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/magic-pdf.template.json"
    config_file_name = "magic-pdf.json"
    home_dir = os.path.expanduser("~")
    config_file = os.path.join(home_dir, config_file_name)

    json_mods = {
        "models-dir": model_dir,
        "layoutreader-model-dir": layoutreader_model_dir,
    }

    download_and_modify_json(json_url, config_file, json_mods)
    print(f"The configuration file has been configured successfully, the path is: {config_file}")


if __name__ == "__main__":
    download_and_modify_json()
