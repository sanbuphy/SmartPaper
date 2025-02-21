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
