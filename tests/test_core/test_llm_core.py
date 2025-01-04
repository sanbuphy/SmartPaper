import os
import sys


# 添加项目根目录到sys.path，确保可以导入SmartPaper模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from SmartPaper.core.llm_core import get_llm_response, get_llm_response_with_callback, get_llm_response_with_history_callback

# 使用示例
if __name__ == "__main__":
    # 简单调用示例
    response = get_llm_response("你好，请介绍一下你自己。", model="Qwen/Qwen3-8B", temperature=0.8)
    print("简单调用结果:", response)
    
    # 流式回调示例
    def print_callback(chunk: str):
        print(chunk, end="", flush=True)
    
    print("\n\n流式回调示例:")
    get_llm_response_with_callback("请简要介绍Transformer模型架构", callback=print_callback, model="Qwen/Qwen3-8B")
    
    # 历史对话示例
    print("\n\n历史对话示例:")
    messages = [
        {"role": "system", "content": "你是一个有用的AI助手。"},
        {"role": "user", "content": "什么是大语言模型？"},
        {"role": "assistant", "content": "大语言模型（Large Language Model，简称LLM）是一类基于深度学习的自然语言处理模型，通过在大规模文本语料库上训练，能够理解和生成人类语言。"},
        {"role": "user", "content": "它们有哪些应用？"}
    ]
    
    def history_callback(chunk: str):
        print(chunk, end="", flush=True)
    
    get_llm_response_with_history_callback(messages, callback=history_callback, model="Qwen/Qwen3-8B")