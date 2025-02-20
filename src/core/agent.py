from typing import Dict, List
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import json
from ..utils.llm_adapter import create_llm_adapter


class PaperAgent:
    def __init__(self, config: dict):
        """初始化论文分析Agent

        Args:
            config (dict): 配置信息
        """
        self.config = config
        self.llm = create_llm_adapter(config["llm"])
        self.memory = []
        self.max_iterations = config["agent"]["max_iterations"]
        self.memory_window = config["agent"]["memory_window"]

    def analyze(self, text_content: str) -> Dict:
        """智能分析论文内容

        Args:
            text_content (str): 论文文本内容

        Returns:
            Dict: 分析结果
        """
        # 初始化系统提示词
        system_prompt = """你是一个专业的论文分析助手。你的任务是深入分析论文内容，并提供以下方面的见解：
1. 论文的主要贡献和创新点
2. 研究方法论的评估
3. 实验结果的分析
4. 潜在的应用场景
5. 局限性和未来工作方向

请以结构化的方式组织你的分析，确保内容清晰且易于理解。"""

        self.memory = [SystemMessage(content=system_prompt)]

        # 添加论文内容到对话
        self.memory.append(HumanMessage(content=f"请分析以下论文内容：\n\n{text_content}"))

        # 开始多轮分析
        analysis_result = {}
        for _ in range(self.max_iterations):
            response = self.llm(self.memory[-self.memory_window :])
            self.memory.append(AIMessage(content=response.content))

            # 尝试解析结构化结果
            try:
                if self._is_analysis_complete(response.content):
                    analysis_result = self._parse_final_result(response.content)
                    break
            except:
                continue

            # 添加后续提问
            follow_up = self._generate_follow_up_question(response.content)
            if not follow_up:
                break

            self.memory.append(HumanMessage(content=follow_up))

        return analysis_result or {"result": self.memory[-2].content}

    def _is_analysis_complete(self, content: str) -> bool:
        """检查分析是否完成

        Args:
            content (str): 响应内容

        Returns:
            bool: 是否完成分析
        """
        required_sections = ["贡献", "方法", "结果", "应用", "局限"]
        return all(section.lower() in content.lower() for section in required_sections)

    def _parse_final_result(self, content: str) -> Dict:
        """解析最终结果为结构化格式

        Args:
            content (str): 响应内容

        Returns:
            Dict: 结构化的分析结果
        """
        return {
            "result": content,
            "structured_analysis": {
                "contributions": self._extract_section(content, "贡献"),
                "methodology": self._extract_section(content, "方法"),
                "results": self._extract_section(content, "结果"),
                "applications": self._extract_section(content, "应用"),
                "limitations": self._extract_section(content, "局限"),
            },
        }

    def _generate_follow_up_question(self, content: str) -> str:
        """生成后续问题

        Args:
            content (str): 当前响应内容

        Returns:
            str: 后续问题
        """
        if not self._is_analysis_complete(content):
            missing_sections = []
            sections = {
                "贡献": "论文的主要贡献和创新点",
                "方法": "研究方法论",
                "结果": "实验结果",
                "应用": "潜在的应用场景",
                "局限": "局限性和未来工作",
            }

            for key, description in sections.items():
                if key.lower() not in content.lower():
                    missing_sections.append(description)

            if missing_sections:
                return f"请补充分析以下方面的内容：\n" + "\n".join(
                    f"- {section}" for section in missing_sections
                )

        return ""

    def _extract_section(self, content: str, section_name: str) -> str:
        """从内容中提取特定部分

        Args:
            content (str): 完整内容
            section_name (str): 部分名称

        Returns:
            str: 提取的内容
        """
        try:
            # 简单的基于关键词的提取
            start_idx = content.lower().find(section_name.lower())
            if start_idx == -1:
                return ""

            # 找到下一个部分的开始
            next_section_idx = float("inf")
            for section in ["贡献", "方法", "结果", "应用", "局限"]:
                if section.lower() == section_name.lower():
                    continue
                idx = content.lower().find(section.lower(), start_idx + 1)
                if idx != -1:
                    next_section_idx = min(next_section_idx, idx)

            if next_section_idx == float("inf"):
                return content[start_idx:].strip()
            return content[start_idx:next_section_idx].strip()
        except:
            return ""

    def update_api_key(self, api_key: str):
        """更新API密钥

        Args:
            api_key (str): 新的API密钥
        """
        self.llm.update_api_key(api_key)
