"""
#### 使用说明：

此代码用于将文件名转换为绝对路径。可以选择性地提供基础目录，如果不提供，则默认使用当前工作目录。如果提供了绝对路径，则会直接验证文件是否存在并返回其绝对路径。

#### 主要功能：
- 将相对路径转换为绝对路径。
- 如果提供了基础目录，则基于该目录计算文件的绝对路径。
- 如果文件或目录不存在，抛出异常。

#### 参数说明：

- **get_abs_path函数**：
  - `file_name (str)`: 文件名，支持相对路径或绝对路径。
  - `base_dir (str, optional)`: 基础目录的绝对路径，默认为None时使用当前工作目录。
  - **返回值**：文件的绝对路径。

#### 注意事项：
- `base_dir` 必须是一个绝对路径，如果指定了，则必须验证其存在。
- 如果文件名已经是绝对路径，程序将验证该路径是否存在。
- 如果文件或目录不存在，函数会抛出 `ValueError` 异常。

#### 更多信息：
- 本代码适用于需要根据相对路径和基础目录计算文件的绝对路径的应用场景。

"""

import os


def get_abs_path(file_name, base_dir=None):
    """
    将文件名转换为绝对路径。如果提供了base_dir，则基于该目录；否则使用当前工作目录。

    参数:
        file_name (str): 文件名（可以是相对路径或绝对路径）
        base_dir (str, optional): 基础目录的绝对路径，默认为None时使用当前工作目录
    返回:
        str: 文件的绝对路径
    异常:
        ValueError: 如果文件不存在或路径无效
    """
    # 如果已经传入绝对路径，直接验证并返回
    if os.path.isabs(file_name):
        if os.path.exists(file_name):
            return os.path.abspath(file_name)
        else:
            raise ValueError(f"文件不存在: {file_name}")

    # 如果未指定base_dir，使用当前工作目录
    if base_dir is None:
        base_dir = os.getcwd()
    elif not os.path.isabs(base_dir):
        raise ValueError("base_dir 必须是绝对路径")

    # 确保base_dir存在
    if not os.path.exists(base_dir):
        raise ValueError(f"基础目录不存在: {base_dir}")

    # 组合路径并转换为绝对路径
    absolute_path = os.path.abspath(os.path.join(base_dir, file_name))

    # 验证文件是否存在
    if not os.path.exists(absolute_path):
        raise ValueError(f"文件不存在: {absolute_path}")

    return absolute_path
