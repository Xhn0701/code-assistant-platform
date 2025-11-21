"""
依赖注入模块
提供 FastAPI 的依赖注入函数。
"""

import logging
from functools import lru_cache
from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends

from app.config import Settings, get_settings
from app.services.code_indexer import CodeIndexer
from app.services.code_loader import CodeLoader
from app.services.code_splitter import CodeSplitter
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore import VectorStoreService
from app.agents.qa_agent import QaAgent

logger = logging.getLogger(__name__)


# ========== Redis 依赖 ==========


async def get_redis_client(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[redis.Redis, None]:
    """获取 Redis 客户端（异步）。"""
    client = None
    try:
        client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=settings.redis_timeout,
        )
        # 测试连接
        await client.ping()
        logger.debug("Redis 连接成功")
        yield client
    except Exception as exc:  # pragma: no cover - 网络异常分支
        logger.error("Redis 连接失败: %s", exc)
        raise
    finally:
        if client:
            await client.close()
            logger.debug("Redis 连接已关闭")


# ========== 配置依赖 ==========


def get_app_config() -> Settings:
    """获取应用配置（get_settings 的别名，提供更语义化的命名）。"""
    return get_settings()


# ========== 日志依赖 ==========


def get_logger(name: str = __name__) -> logging.Logger:
    """获取日志记录器。"""
    return logging.getLogger(name)


# ========== Agent / 向量检索相关依赖 ==========


def get_embedding_service() -> EmbeddingService:
    """Embedding 服务实例。

    说明：不使用 lru_cache，便于测试中通过 patch OpenAIEmbeddings。"""
    return EmbeddingService()


def get_vector_store_service() -> VectorStoreService:
    """向量存储服务实例。"""
    return VectorStoreService(get_embedding_service())


def get_code_indexer() -> CodeIndexer:
    """代码索引服务实例。"""
    settings = get_settings()
    loader = CodeLoader(max_file_size=settings.index_max_file_size)
    splitter = CodeSplitter(
        chunk_size=settings.index_chunk_size,
        chunk_overlap=settings.index_chunk_overlap,
    )
    return CodeIndexer(
        loader=loader,
        splitter=splitter,
        vectorstore=get_vector_store_service(),
    )


@lru_cache()
def get_qa_agent() -> QaAgent:
    """RAG 问答 Agent 单例。"""
    return QaAgent(vectorstore=get_vector_store_service())


__all__ = [
    "get_redis_client",
    "get_app_config",
    "get_logger",
    "get_embedding_service",
    "get_vector_store_service",
    "get_code_indexer",
    "get_qa_agent",
]
