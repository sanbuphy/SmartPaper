#!/usr/bin/env python  
# -*- coding: utf-8 -*-
# author：筱可
# 2025/2/27
"""
#### 使用说明：
通过命令行或导入模块方式调用detect_layout函数，可以检测文档图片的布局。

#### 主要功能：
1. 使用PaddlePaddle的布局分析模型检测文档布局
2. 支持将检测结果保存为图像和JSON格式
3. 支持NMS过滤

#### 参数说明：
detect_layout函数参数：
    image_path (str): 输入图像的路径
    model_name (str): 模型名称，默认为"PP-DocLayout-L"
    batch_size (int): 批处理大小，默认为1
    layout_nms (bool): 是否使用NMS处理布局结果，默认为True
    save_path (str): 保存结果图像的路径，默认为"./output/"
    json_path (str): 保存JSON结果的路径，默认为"./output/res.json"
返回值：
    list: 检测结果列表

#### 注意事项：
依赖PaddleX库，使用前请确保已正确安装paddlex及其依赖

1.

# cpu

python -m pip install paddlepaddle==3.0.0rc0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/

# gpu，该命令仅适用于 CUDA 版本为 11.8 的机器环境
python -m pip install paddlepaddle-gpu==3.0.0rc0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

# gpu，该命令仅适用于 CUDA 版本为 12.3 的机器环境
python -m pip install paddlepaddle-gpu==3.0.0rc0 -i https://www.paddlepaddle.org.cn/packages/stable/cu123/

---

2. 

pip install https://paddle-model-ecology.bj.bcebos.com/paddlex/whl/paddlex-3.0.0b2-py3-none-any.whl

#### 参考资料
https://paddlepaddle.github.io/PaddleX/main/installation/installation.html#1

"""

def detect_layout(image_path,
                  model_name="PP-DocLayout-L",
                  batch_size=1, 
                  layout_nms=True, 
                  save_path="./output/result.png", 
                  json_path="./output/res.json"):
    """
    使用PP-DocLayout模型检测文档布局
    
    Args:
        image_path (str): 输入图像的路径
        model_name (str): 模型名称
        batch_size (int): 批处理大小
        layout_nms (bool): 是否使用NMS处理布局结果
        save_path (str): 保存结果图像的路径
        json_path (str): 保存JSON结果的路径
    
    Returns:
        list: 检测结果列表
    """
    from paddlex import create_model
    
    # 创建模型
    model = create_model(model_name=model_name)
    
    # 预测
    output = model.predict(image_path, batch_size=batch_size, layout_nms=layout_nms)
    
    # 处理结果
    for res in output:
        res.print()
        res.save_to_img(save_path=save_path)
        res.save_to_json(save_path=json_path)
    
    return output