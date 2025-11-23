"""
统一响应格式模块
与Java服务的Result类保持一致的响应结构
"""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应模型

    对应Java端的Result类结构：
    {
        "code": 200,
        "message": "操作成功",
        "data": {...},
        "timestamp": "2025-11-16T17:00:00.000",
        "success": true
    }
    """

    code: int = Field(description="状态码，200表示成功")
    message: str = Field(description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
        description="响应时间戳"
    )
    success: bool = Field(description="操作是否成功")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "message": "操作成功",
                "data": {"key": "value"},
                "timestamp": "2025-11-16T17:00:00.000",
                "success": True,
            }
        }
    )

    @classmethod
    def ok(cls, data: Any = None, message: str = "操作成功", code: int = 200) -> "ResponseModel":
        """
        创建成功响应

        Args:
            data: 响应数据
            message: 响应消息
            code: 状态码

        Returns:
            ResponseModel: 统一响应对象
        """
        return cls(
            code=code,
            message=message,
            data=data,
            success=True
        )

    @classmethod
    def fail(cls, message: str, code: int = 500, data: Any = None) -> "ResponseModel":
        """
        创建错误响应

        Args:
            message: 错误消息
            code: 错误码
            data: 额外的错误数据

        Returns:
            ResponseModel: 统一响应对象
        """
        return cls(
            code=code,
            message=message,
            data=data,
            success=False
        )


def create_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200
) -> ResponseModel:
    """
    创建成功响应

    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码

    Returns:
        ResponseModel: 统一响应对象
    """
    return ResponseModel(
        code=code,
        message=message,
        data=data,
        success=True
    )


def create_error_response(
    message: str,
    code: int = 500,
    data: Any = None
) -> ResponseModel:
    """
    创建错误响应

    Args:
        message: 错误消息
        code: 错误码
        data: 额外的错误数据

    Returns:
        ResponseModel: 统一响应对象
    """
    return ResponseModel(
        code=code,
        message=message,
        data=data,
        success=False
    )


# 常用响应消息
class ResponseMessage:
    """响应消息常量"""

    # 成功消息
    SUCCESS = "操作成功"
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"

    # 错误消息
    INTERNAL_ERROR = "服务器内部错误"
    PARAM_ERROR = "参数错误"
    NOT_FOUND = "资源不存在"
    UNAUTHORIZED = "未授权访问"
    FORBIDDEN = "权限不足"
    RATE_LIMIT_EXCEEDED = "请求过于频繁，请稍后再试"

    # Agent相关
    INDEX_IN_PROGRESS = "代码索引进行中"
    INDEX_COMPLETED = "代码索引完成"
    INDEX_FAILED = "代码索引失败"
    QUERY_SUCCESS = "查询成功"
    REVIEW_IN_PROGRESS = "代码审查进行中"
    REVIEW_COMPLETED = "代码审查完成"
