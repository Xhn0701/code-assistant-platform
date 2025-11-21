"""
Agent 基类定义。
"""

from abc import ABC, abstractmethod

from app.models.chat import AgentAnswer


class BaseAgent(ABC):
    """Agent 抽象基类。"""

    @abstractmethod
    async def ask(self, project_id: int, question: str, **kwargs) -> AgentAnswer:
        """
        执行一次问答。

        Args:
            project_id: 项目 ID
            question: 用户问题
        """

