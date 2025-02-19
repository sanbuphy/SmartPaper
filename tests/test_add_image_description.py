import sys
import  os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.add_image_description import add_image_description



if __name__ == "__main__":
    # 设置目标文件路径并执行主程序
    target = r"C:\Users\k\Documents\project\programming_project\python_project\importance\SmartPaper\tests\如何阅读一本书-output-884dbaf7-2aad-47f6-af02-05a777b3bc3f\如何阅读一本书-output.md"
    add_image_description(target)
