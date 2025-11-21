"""
Embedding 服务封装。

当前使用 OpenAI text-embedding-3-small 模型，后续可以替换为本地模型。
"""

import logging
from typing import List

from langchain_openai import OpenAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.core.exceptions import AgentErrorCode, AgentException

logger = logging.getLogger(__name__)


class EmbeddingService:
    """封装向量生成逻辑，便于后续切换实现。"""

    def __init__(self) -> None:
        try:
            base_url = settings.openai_api_base or None

            # 针对 Gitee Serverless（ai.gitee.com）做兼容处理：
            # - 禁用 tiktoken 预分词，直接发送原始文本
            # - 强制使用 encoding_format="float"，符合其接口文档
            if base_url and "ai.gitee.com" in base_url:
                # Gitee Serverless：直接发送原始文本，避免本地 token 化依赖
                self._embedding = OpenAIEmbeddings(
                    model=settings.openai_embedding_model,
                    api_key=settings.openai_api_key or None,
                    base_url=base_url,
                    check_embedding_ctx_length=False,  # 不做本地长度切分，直接传原文
                    encoding_format="float",          # 按 Gitee 文档使用 float 格式
                )
            else:
                self._embedding = OpenAIEmbeddings(
                    model=settings.openai_embedding_model,
                    api_key=settings.openai_api_key or None,
                    base_url=base_url,
                )

            logger.info(
                "EmbeddingService 初始化完成，模型=%s",
                settings.openai_embedding_model,
            )
        except Exception as exc:  # pragma: no cover - 初始化异常较少发生
            logger.error("初始化 OpenAIEmbeddings 失败: %s", exc, exc_info=True)
            raise AgentException(
                AgentErrorCode.OPENAI_API_ERROR,
                "初始化 Embedding 客户端失败",
                data={"error": str(exc)},
            ) from exc

    @property
    def embedding(self) -> OpenAIEmbeddings:
        """返回底层 LangChain Embedding 对象，用于 VectorStore。"""
        return self._embedding

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量生成文档向量。"""
        try:
            return self._embedding.embed_documents(texts)
        except Exception as exc:
            logger.error("Embedding 文档失败: %s", exc, exc_info=True)
            raise AgentException(
                AgentErrorCode.EMBEDDING_ERROR,
                "Embedding 文档失败",
                data={"error": str(exc)},
            ) from exc

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def embed_query(self, text: str) -> List[float]:
        """生成查询向量。"""
        try:
            return self._embedding.embed_query(text)
        except Exception as exc:
            logger.error("Embedding 查询失败: %s", exc, exc_info=True)
            raise AgentException(
                AgentErrorCode.EMBEDDING_ERROR,
                "Embedding 查询失败",
                data={"error": str(exc)},
            ) from exc


__all__ = ["EmbeddingService"]

