"""
API v1 版本路由聚合。
"""

from fastapi import APIRouter

from . import chat, health, index

# 创建 v1 路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(health.router, tags=["健康检查"])
api_router.include_router(chat.router, prefix="/chat", tags=["代码问答"])
api_router.include_router(index.router, prefix="/index", tags=["代码索引"])

__all__ = ["api_router"]

