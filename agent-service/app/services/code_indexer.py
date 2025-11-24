"""
代码索引协调服务。

负责调用 CodeLoader / CodeSplitter / VectorStoreService 完成索引流程，
并管理索引状态（MVP 版本使用内存 + Chroma 推断）。
"""

import logging
from typing import Dict, Optional

from langchain_core.documents import Document

from app.config import settings
from app.core.exceptions import AgentErrorCode, AgentException
from app.models.code import CodeChunk
from app.models.index import (
    IndexRepositoryRequest,
    IndexRepositoryResult,
    IndexStatus,
    IndexStatusResponse,
)
from app.services.code_loader import CodeLoader
from app.services.code_splitter import CodeSplitter
from app.services.vectorstore import VectorStoreService

logger = logging.getLogger(__name__)


class IndexStatusStore:
    """
    索引状态管理。

    当前使用内存存储 + Chroma 推断，后续可迁移到 Redis。
    """

    def __init__(self, vectorstore: VectorStoreService) -> None:
        self._vectorstore = vectorstore
        self._memory_store: Dict[int, IndexStatusResponse] = {}

    def set_status(
        self,
        project_id: int,
        status: IndexStatus,
        total_files: int = 0,
        indexed_files: int = 0,
        error_message: Optional[str] = None,
    ) -> None:
        """更新内存状态。"""
        self._memory_store[project_id] = IndexStatusResponse(
            project_id=project_id,
            status=status,
            total_files=total_files,
            indexed_files=indexed_files,
            error_message=error_message,
        )

    def get_status(self, project_id: int) -> Optional[IndexStatusResponse]:
        """
        获取索引状态。

        优先返回内存记录；如无，则基于 Chroma 集合推断：
        - 如果存在集合且文档数 > 0，则视作 COMPLETED（total_files 近似为 doc_count）
        - 否则返回 None（表示未索引）
        """
        if project_id in self._memory_store:
            return self._memory_store[project_id]

        # 内存无记录，尝试基于 Chroma 推断
        try:
            stats = self._vectorstore.get_collection_stats(project_id)
            doc_count = stats.get("doc_count", 0) or 0
            if doc_count > 0:
                return IndexStatusResponse(
                    project_id=project_id,
                    status=IndexStatus.COMPLETED,
                    total_files=doc_count,
                    indexed_files=doc_count,
                    error_message=None,
                )
        except AgentException:
            # 向量库错误在上层统一处理
            logger.warning("根据 Chroma 推断索引状态失败，project_id=%s", project_id)

        return None

    def get_collection_stats(self, project_id: int) -> Dict:
        """
        获取底层向量集合的统计信息。

        目前直接委托给 VectorStoreService，主要用于调试型 API。
        """
        return self._vectorstore.get_collection_stats(project_id)


class CodeIndexer:
    """代码索引协调服务。"""

    def __init__(
        self,
        loader: CodeLoader,
        splitter: CodeSplitter,
        vectorstore: VectorStoreService,
    ) -> None:
        self._loader = loader
        self._splitter = splitter
        self._vectorstore = vectorstore
        self._status_store = IndexStatusStore(vectorstore)

    def index_repository(self, request: IndexRepositoryRequest) -> IndexRepositoryResult:
        """
        同步索引指定项目的仓库。
        """
        project_id = request.project_id
        repo_path = request.repository_url

        logger.info("[项目 %s] 开始索引仓库: %s", project_id, repo_path)

        # 1. 设置状态为 INDEXING
        self._status_store.set_status(
            project_id=project_id,
            status=IndexStatus.INDEXING,
            total_files=0,
            indexed_files=0,
        )

        try:
            # 2. 加载代码文件
            files = self._loader.load_repository(project_id, repo_path)
            total_files = len(files)
            logger.info("[项目 %s] 共加载 %d 个文件", project_id, total_files)

            # 3. 分块
            all_chunks: list[CodeChunk] = []
            for idx, code_file in enumerate(files):
                chunks = self._splitter.split_code_file(code_file)
                all_chunks.extend(chunks)

                # 每 10% 输出一次进度日志
                if total_files > 0 and (idx + 1) % max(1, total_files // 10) == 0:
                    progress = (idx + 1) / total_files * 100
                    logger.info(
                        "[项目 %s] 分块进度: %.0f%% (%d/%d)",
                        project_id,
                        progress,
                        idx + 1,
                        total_files,
                    )

            logger.info(
                "[项目 %s] 分块完成，共生成 %d 个代码块",
                project_id,
                len(all_chunks),
            )

            # 4. 转换为 Document
            documents: list[Document] = [chunk.to_document() for chunk in all_chunks]

            # 5. 重建集合并批量写入
            self._vectorstore.reset_collection(project_id)

            batch_size = settings.index_batch_size
            total_docs = len(documents)
            for i in range(0, total_docs, batch_size):
                batch = documents[i : i + batch_size]
                self._vectorstore.upsert_documents_batch(project_id, batch)

                progress = min(100, (i + len(batch)) / max(1, total_docs) * 100)
                logger.info(
                    "[项目 %s] 索引进度: %.0f%% (%d/%d)",
                    project_id,
                    progress,
                    i + len(batch),
                    total_docs,
                )

            # 6. 设置状态为 COMPLETED
            self._status_store.set_status(
                project_id=project_id,
                status=IndexStatus.COMPLETED,
                total_files=total_files,
                indexed_files=total_files,
            )

            logger.info("[项目 %s] 索引完成", project_id)

            return IndexRepositoryResult(
                project_id=project_id,
                status=IndexStatus.COMPLETED,
                total_files=total_files,
                indexed_files=total_files,
                error_message=None,
            )
        except AgentException as exc:
            # 业务异常：透传，并更新状态
            logger.error(
                "[项目 %s] 索引失败（业务异常）: %s", project_id, exc.message, exc_info=True
            )
            self._status_store.set_status(
                project_id=project_id,
                status=IndexStatus.FAILED,
                total_files=0,
                indexed_files=0,
                error_message=exc.message,
            )
            raise
        except Exception as exc:
            # 未预期异常：统一包装成 INDEX_ERROR
            logger.error(
                "[项目 %s] 索引失败（系统异常）: %s", project_id, exc, exc_info=True
            )
            self._status_store.set_status(
                project_id=project_id,
                status=IndexStatus.FAILED,
                total_files=0,
                indexed_files=0,
                error_message=str(exc),
            )
            raise AgentException(
                AgentErrorCode.INDEX_ERROR,
                "代码索引失败",
                data={"error": str(exc)},
            ) from exc

    def get_index_status(self, project_id: int) -> IndexStatusResponse:
        """
        查询索引状态。

        如果既无内存记录又无法从 Chroma 推断，则抛出 INDEX_NOT_READY。
        """
        status = self._status_store.get_status(project_id)
        if status is None:
            raise AgentException(
                AgentErrorCode.INDEX_NOT_READY,
                "代码索引未完成，请先调用索引接口",
            )
        return status

    def get_collection_stats(self, project_id: int) -> Dict:
        """
        返回指定项目的向量集合统计信息。

        用于调试和监控接口，避免直接暴露内部存储实现。
        """
        return self._status_store.get_collection_stats(project_id)


__all__ = ["CodeIndexer", "IndexStatusStore"]
