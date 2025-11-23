"""
异常处理模块
定义 Agent 服务的自定义异常和错误码。
"""

from enum import Enum
from typing import Any, Optional


class AgentErrorCode(int, Enum):
    """Agent 服务错误码。

    数值区间规划（与 Java ResultCode 语义对齐）：
    - 1000-1999：通用错误
    - 2000-2999：Agent / 索引 / 向量库 / LLM 相关错误
    - 4000-4999：外部服务错误
    """

    # ========== 通用错误 (1000-1999) ==========
    SUCCESS = 200
    PARAM_ERROR = 1000
    INTERNAL_ERROR = 1001
    NOT_FOUND = 1002
    UNAUTHORIZED = 1003
    FORBIDDEN = 1004
    RATE_LIMIT_EXCEEDED = 1005

    # ========== Agent / 索引相关错误 (2000-2999) ==========
    REPOSITORY_ERROR = 2000      # 仓库访问错误（路径无效 / 无权限）
    INDEX_ERROR = 2001           # 索引过程失败
    INDEX_NOT_READY = 2002       # 索引未完成 / 不存在
    INDEX_IN_PROGRESS = 2003     # 索引进行中

    VECTOR_STORE_ERROR = 2100    # 向量存储错误（Chroma 操作失败）
    EMBEDDING_ERROR = 2101       # Embedding 生成失败

    OPENAI_API_ERROR = 2200      # OpenAI API 调用失败
    LLM_ERROR = 2201             # 大模型调用失败
    QUERY_ERROR = 2202           # 查询失败（预留，当前未使用）

    REVIEW_ERROR = 2300          # 代码审查错误

    # ========== 外部服务错误 (4000-4099) ==========
    JAVA_SERVICE_ERROR = 4000    # Java 服务调用错误
    REDIS_ERROR = 4001           # Redis 错误


class AgentException(Exception):
    """Agent 服务自定义异常。

    用于业务逻辑中需要明确返回错误码和消息的场景。
    """

    def __init__(
        self,
        error_code: AgentErrorCode,
        message: Optional[str] = None,
        data: Optional[Any] = None,
    ) -> None:
        """初始化异常。

        Args:
            error_code: 错误码枚举值
            message: 自定义错误消息（如果为 None，使用默认消息）
            data: 额外的错误数据
        """
        self.error_code = error_code
        self.message = message or self._get_default_message(error_code)
        self.data = data
        super().__init__(self.message)

    @staticmethod
    def _get_default_message(error_code: AgentErrorCode) -> str:
        """获取错误码对应的默认消息。"""
        messages = {
            AgentErrorCode.PARAM_ERROR: "参数错误",
            AgentErrorCode.INTERNAL_ERROR: "服务器内部错误",
            AgentErrorCode.NOT_FOUND: "资源不存在",
            AgentErrorCode.UNAUTHORIZED: "未授权访问",
            AgentErrorCode.FORBIDDEN: "权限不足",
            AgentErrorCode.RATE_LIMIT_EXCEEDED: "请求过于频繁",
            AgentErrorCode.INDEX_ERROR: "代码索引失败",
            AgentErrorCode.INDEX_NOT_READY: "代码索引未完成，请先调用索引接口",
            AgentErrorCode.REPOSITORY_ERROR: "仓库路径无效或无权限访问",
            AgentErrorCode.VECTOR_STORE_ERROR: "向量存储错误",
            AgentErrorCode.LLM_ERROR: "大模型调用失败",
            AgentErrorCode.REVIEW_ERROR: "代码审查失败",
            AgentErrorCode.EMBEDDING_ERROR: "Embedding 生成失败",
            AgentErrorCode.INDEX_IN_PROGRESS: "代码索引进行中",
            AgentErrorCode.JAVA_SERVICE_ERROR: "Java 服务调用失败",
            AgentErrorCode.REDIS_ERROR: "Redis 连接失败",
            AgentErrorCode.OPENAI_API_ERROR: "OpenAI API 调用失败",
            AgentErrorCode.QUERY_ERROR: "查询失败",
        }
        return messages.get(error_code, "未知错误")

    def to_dict(self) -> dict:
        """转换为字典格式。"""
        return {
            "code": self.error_code.value,
            "message": self.message,
            "data": self.data,
        }


# 便捷异常创建函数

def param_error(message: str = "参数错误", data: Optional[Any] = None) -> "AgentException":
    """参数错误异常。"""
    return AgentException(AgentErrorCode.PARAM_ERROR, message, data)


def internal_error(
    message: str = "服务器内部错误",
    data: Optional[Any] = None,
) -> "AgentException":
    """内部错误异常。"""
    return AgentException(AgentErrorCode.INTERNAL_ERROR, message, data)


def not_found(
    message: str = "资源不存在",
    data: Optional[Any] = None,
) -> "AgentException":
    """资源不存在异常。"""
    return AgentException(AgentErrorCode.NOT_FOUND, message, data)


def unauthorized(
    message: str = "未授权访问",
    data: Optional[Any] = None,
) -> "AgentException":
    """未授权异常。"""
    return AgentException(AgentErrorCode.UNAUTHORIZED, message, data)


def llm_error(
    message: str = "大模型调用失败",
    data: Optional[Any] = None,
) -> "AgentException":
    """LLM 错误异常。"""
    return AgentException(AgentErrorCode.LLM_ERROR, message, data)
