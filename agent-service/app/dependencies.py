"""
依赖注入模块
提供FastAPI的依赖注入函数
"""

import logging
from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


# ========== Redis依赖 ==========

async def get_redis_client(
    settings: Settings = Depends(get_settings)
) -> AsyncGenerator[redis.Redis, None]:
    """
    获取Redis客户端（异步）

    使用方式:
        @app.get("/example")
        async def example(redis_client: redis.Redis = Depends(get_redis_client)):
            await redis_client.set("key", "value")
            return {"status": "ok"}

    Args:
        settings: 配置对象

    Yields:
        redis.Redis: Redis客户端实例
    """
    client = None
    try:
        client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=settings.redis_timeout
        )
        # 测试连接
        await client.ping()
        logger.debug("Redis连接成功")
        yield client
    except Exception as e:
        logger.error(f"Redis连接失败: {e}")
        raise
    finally:
        if client:
            await client.close()
            logger.debug("Redis连接已关闭")


# ========== 配置依赖 ==========

def get_app_config() -> Settings:
    """
    获取应用配置

    这是get_settings的别名，提供更语义化的命名
    """
    return get_settings()


# ========== 日志依赖 ==========

def get_logger(name: str = __name__) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


# ========== 未来扩展 ==========

# TODO: Phase 4 - 添加向量数据库依赖
# async def get_vector_store() -> AsyncGenerator[VectorStore, None]:
#     """获取向量存储客户端"""
#     pass

# TODO: Phase 4 - 添加LLM依赖
# def get_llm() -> LLM:
#     """获取LLM实例"""
#     pass

# TODO: Phase 3 - 添加Java服务客户端依赖
# async def get_java_client() -> AsyncGenerator[JavaServiceClient, None]:
#     """获取Java服务客户端"""
#     pass
