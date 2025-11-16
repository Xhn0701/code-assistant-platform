"""
健康检查接口
提供服务健康状态检查功能
"""

import logging
from datetime import datetime
from typing import Dict

import redis.asyncio as redis
from fastapi import APIRouter, Depends, status

from app.config import Settings, get_settings
from app.core.response import ResponseModel, create_response, create_error_response
from app.dependencies import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    response_model=ResponseModel[Dict],
    status_code=status.HTTP_200_OK,
    summary="健康检查",
    description="检查服务运行状态和依赖组件连接状态"
)
async def health_check(
    settings: Settings = Depends(get_settings),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> ResponseModel:
    """
    健康检查接口

    检查项:
    - 服务运行状态
    - Redis连接状态
    - 配置加载状态

    Returns:
        ResponseModel: 包含健康状态信息的响应
    """
    health_data = {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "UP",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "components": {}
    }

    # 检查Redis连接
    try:
        await redis_client.ping()
        health_data["components"]["redis"] = {
            "status": "UP",
            "host": settings.redis_host,
            "port": settings.redis_port,
            "db": settings.redis_db
        }
        logger.debug("Redis健康检查: UP")
    except Exception as e:
        logger.error(f"Redis健康检查失败: {e}")
        health_data["components"]["redis"] = {
            "status": "DOWN",
            "error": str(e)
        }
        health_data["status"] = "DEGRADED"  # 服务降级但仍可用

    # 检查配置加载
    health_data["components"]["config"] = {
        "status": "UP" if settings.openai_api_key else "WARNING",
        "warning": "OpenAI API Key未配置" if not settings.openai_api_key else None
    }

    # TODO: Phase 4 - 添加ChromaDB健康检查
    # health_data["components"]["chromadb"] = {...}

    return create_response(
        data=health_data,
        message="健康检查成功"
    )


@router.get(
    "/ready",
    response_model=ResponseModel[Dict],
    status_code=status.HTTP_200_OK,
    summary="就绪检查",
    description="检查服务是否就绪接受请求"
)
async def readiness_check(
    redis_client: redis.Redis = Depends(get_redis_client)
) -> ResponseModel:
    """
    就绪检查接口

    检查所有必需的依赖是否就绪：
    - Redis必须可用

    Returns:
        ResponseModel: 就绪状态响应

    Raises:
        HTTPException: 当服务未就绪时返回503
    """
    try:
        # Redis必须可用
        await redis_client.ping()

        return create_response(
            data={"ready": True},
            message="服务就绪"
        )
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        return create_error_response(
            message=f"服务未就绪: {str(e)}",
            code=503
        )


@router.get(
    "/ping",
    response_model=ResponseModel[Dict],
    status_code=status.HTTP_200_OK,
    summary="快速Ping",
    description="最轻量的健康检查，仅检查服务是否响应"
)
async def ping() -> ResponseModel:
    """
    Ping接口 - 最简单的健康检查

    不检查任何依赖，仅确认服务进程存活

    Returns:
        ResponseModel: Pong响应
    """
    return create_response(
        data={"pong": True},
        message="pong"
    )
