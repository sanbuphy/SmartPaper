# import streamlit as st
from loguru import logger
from src.core.reader import SmartPaper
from src.prompts.prompt_library import list_prompts
import os

def process_paper(url: str, prompt_name: str = 'yuanbao'):
    """处理论文

    Args:
        url (str): 论文URL
        prompt_name (str): 提示词模板名称
    """
    try:

        # 初始化SmartPaper
        reader = SmartPaper(output_format='markdown')
        logger.info(f"使用提示词模板: {prompt_name}")
        
        # 处理论文
        result = reader.process_paper_url(url, mode='prompt', prompt_name=prompt_name)
        
        # 创建输出目录
        output_dir = 'outputs'
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存结果
        output_file = os.path.join(output_dir, f'analysis_prompt_{prompt_name}.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['result'])
            
        logger.info(f"分析结果已保存到: {output_file}")
        return result['result']
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        # st.error(f"处理失败: {str(e)}")
        return None

# def main():
#     """主函数"""
#     st.title("论文分析工具")
#     st.session_state.paper_analysis_result = ""
#     # 侧边栏设置
#     with st.sidebar:
#         st.header("设置")
#
#         # 显示可用的提示词模板
#         # st.write("可用的提示词模板:")
#         prompt_names = list_prompts()
#         # for name, desc in prompt_names.items():
#         #     st.write(f"- {name}: {desc}")
#         st.write("")
#
#         # 创建输入框
#         url = st.text_input("论文URL", "https://arxiv.org/pdf/2305.12002")
#         prompt_name = st.selectbox("提示词模板名称", list(prompt_names.keys()), index=0)
#
#         # 创建按钮
#         if st.button("开始分析"):
#             with st.spinner("正在分析论文..."):
#                 st.session_state.paper_analysis_result = process_paper(url, prompt_name)
#
#     if st.session_state.paper_analysis_result:
#         result = st.session_state.paper_analysis_result
#         st.markdown(result)

if __name__ == '__main__':
    result = process_paper("https://arxiv.org/pdf/2305.12002", list(list_prompts().keys())[0])
    print(result)
    # main()
