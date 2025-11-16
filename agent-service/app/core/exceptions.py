"""
异常处理模块
定义Agent服务的自定义异常和错误码
"""

from enum import Enum
from typing import Any, Optional


class AgentErrorCode(int, Enum):
    """
    Agent服务错误码
    与Java服务的ResultCode保持一致的编码规范
    """

    # ========== 通用错误 (1000-1999) ==========
    SUCCESS = 200
    PARAM_ERROR = 1000
    INTERNAL_ERROR = 1001
    NOT_FOUND = 1002
    UNAUTHORIZED = 1003
    FORBIDDEN = 1004
    RATE_LIMIT_EXCEEDED = 1005

    # ========== Agent相关错误 (3000-3999) ==========
    INDEX_ERROR = 3001                 # 索引错误
    INDEX_NOT_READY = 3002             # 索引未就绪
    REPOSITORY_ERROR = 3003            # 仓库访问错误
    VECTOR_STORE_ERROR = 3004          # 向量存储错误
    LLM_ERROR = 3005                   # LLM调用错误
    REVIEW_ERROR = 3006                # 代码审查错误
    EMBEDDING_ERROR = 3007             # Embedding生成错误

    # ========== 外部服务错误 (4000-4999) ==========
    JAVA_SERVICE_ERROR = 4001          # Java服务调用错误
    REDIS_ERROR = 4002                 # Redis错误
    OPENAI_API_ERROR = 4003            # OpenAI API错误


class AgentException(Exception):
    """
    Agent服务自定义异常

    用于业务逻辑中需要明确返回错误码和消息的场景
    """

    def __init__(
        self,
        error_code: AgentErrorCode,
        message: Optional[str] = None,
        data: Optional[Any] = None
    ):
        """
        初始化异常

        Args:
            error_code: 错误码枚举
            message: 自定义错误消息（如果为None，使用默认消息）
            data: 额外的错误数据
        """
        self.error_code = error_code
        self.message = message or self._get_default_message(error_code)
        self.data = data
        super().__init__(self.message)

    @staticmethod
    def _get_default_message(error_code: AgentErrorCode) -> str:
        """获取错误码对应的默认消息"""
        messages = {
            AgentErrorCode.PARAM_ERROR: "参数错误",
            AgentErrorCode.INTERNAL_ERROR: "服务器内部错误",
            AgentErrorCode.NOT_FOUND: "资源不存在",
            AgentErrorCode.UNAUTHORIZED: "未授权访问",
            AgentErrorCode.FORBIDDEN: "权限不足",
            AgentErrorCode.RATE_LIMIT_EXCEEDED: "请求过于频繁",

            AgentErrorCode.INDEX_ERROR: "代码索引失败",
            AgentErrorCode.INDEX_NOT_READY: "代码索引未就绪",
            AgentErrorCode.REPOSITORY_ERROR: "仓库访问失败",
            AgentErrorCode.VECTOR_STORE_ERROR: "向量存储错误",
            AgentErrorCode.LLM_ERROR: "大模型调用失败",
            AgentErrorCode.REVIEW_ERROR: "代码审查失败",
            AgentErrorCode.EMBEDDING_ERROR: "Embedding生成失败",

            AgentErrorCode.JAVA_SERVICE_ERROR: "Java服务调用失败",
            AgentErrorCode.REDIS_ERROR: "Redis连接失败",
            AgentErrorCode.OPENAI_API_ERROR: "OpenAI API调用失败",
        }
        return messages.get(error_code, "未知错误")

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "code": self.error_code.value,
            "message": self.message,
            "data": self.data
        }


# 便捷异常创建函数
def param_error(message: str = "参数错误", data: Any = None) -> AgentException:
    """参数错误异常"""
    return AgentException(AgentErrorCode.PARAM_ERROR, message, data)


def internal_error(message: str = "服务器内部错误", data: Any = None) -> AgentException:
    """内部错误异常"""
    return AgentException(AgentErrorCode.INTERNAL_ERROR, message, data)


def not_found(message: str = "资源不存在", data: Any = None) -> AgentException:
    """资源不存在异常"""
    return AgentException(AgentErrorCode.NOT_FOUND, message, data)


def unauthorized(message: str = "未授权访问", data: Any = None) -> AgentException:
    """未授权异常"""
    return AgentException(AgentErrorCode.UNAUTHORIZED, message, data)


def llm_error(message: str = "大模型调用失败", data: Any = None) -> AgentException:
    """LLM错误异常"""
    return AgentException(AgentErrorCode.LLM_ERROR, message, data)
