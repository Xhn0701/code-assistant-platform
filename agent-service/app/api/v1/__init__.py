"""
API v1版本路由
"""

from fastapi import APIRouter

from . import health

# 创建v1路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(health.router, tags=["健康检查"])

# TODO: Phase 4 - 添加其他路由
# api_router.include_router(chat.router, prefix="/chat", tags=["代码问答"])
# api_router.include_router(index.router, prefix="/index", tags=["代码索引"])
# api_router.include_router(review.router, prefix="/review", tags=["代码审查"])
