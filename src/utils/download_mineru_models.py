"""
#### 使用说明：

此代码用于下载并修改用于MinerU使用的模型配置文件。通过从远程URL下载JSON模板文件，并根据需要修改其中的模型路径配置，最终生成本地配置文件。

#### 主要功能：
- 下载JSON配置文件模板。
- 根据给定的模型路径修改JSON文件内容。
- 将修改后的配置文件保存到本地。

#### 参数说明：
- **download_json函数**：
  - `url (str)`: JSON文件的URL地址。
  - **返回值**：下载的JSON文件内容。

- **download_and_modify_json函数**：
  - 无需参数，函数会自动下载模型并修改JSON文件内容。
  - **返回值**：无返回值，最终会在本地生成配置文件。

#### 注意事项：
- 请确保网络连接正常，因为代码会从远程服务器下载文件。
- `snapshot_download` 用于从指定模型仓库下载模型，确保访问权限正确。
- 修改后的配置文件会存储在当前用户的主目录中，文件名为 `magic-pdf.json`。

#### 更多信息：
- 本代码主要用于在PDF-Extract-Kit项目中配置所需的模型路径，适用于在矿工项目中使用特定的模型。
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
