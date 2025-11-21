"""
代码索引相关 API。
"""

import logging
from typing import Dict

from fastapi import APIRouter, Depends, Path, status

from app.core.response import ResponseMessage, ResponseModel, create_response
from app.dependencies import get_code_indexer
from app.models.index import (
    IndexRepositoryRequest,
    IndexRepositoryResult,
    IndexStatusResponse,
)
from app.services.code_indexer import CodeIndexer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/repository",
    response_model=ResponseModel[IndexRepositoryResult],
    status_code=status.HTTP_200_OK,
    summary="索引代码仓库",
    description="根据项目 ID 和本地仓库路径，对仓库代码进行向量索引。",
)
async def index_repository(
    request: IndexRepositoryRequest,
    indexer: CodeIndexer = Depends(get_code_indexer),
) -> ResponseModel[IndexRepositoryResult]:
    """
    同步索引指定项目的代码仓库。

    说明：
    - 当前仅支持本地仓库路径（repositoryUrl）
    - 重复调用会删除旧向量集合并全量重建索引
    """
    result = indexer.index_repository(request)
    return create_response(
        data=result,
        message=ResponseMessage.INDEX_COMPLETED,
        code=200,
    )


@router.get(
    "/status/{project_id}",
    response_model=ResponseModel[IndexStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="查询索引状态",
    description="根据项目 ID 查询代码索引状态。",
)
async def get_index_status(
    project_id: int = Path(..., description="项目 ID"),
    indexer: CodeIndexer = Depends(get_code_indexer),
) -> ResponseModel[IndexStatusResponse]:
    """
    查询指定项目的索引状态。

    如果索引尚未完成，将抛出业务异常（INDEX_NOT_READY），由全局异常处理中间件统一返回。
    """
    status_obj = indexer.get_index_status(project_id)
    return create_response(
        data=status_obj,
        message=ResponseMessage.QUERY_SUCCESS,
        code=200,
    )


@router.get(
    "/stats/{project_id}",
    response_model=ResponseModel[Dict],
    status_code=status.HTTP_200_OK,
    summary="索引集合统计信息（调试用）",
    description="返回 Chroma 集合中文档数量等统计信息。",
)
async def get_index_stats(
    project_id: int = Path(..., description="项目 ID"),
    indexer: CodeIndexer = Depends(get_code_indexer),
) -> ResponseModel[Dict]:
    """
    调试用接口：返回底层向量集合的文档数等信息。
    """
    # 直接通过 indexer 内部的 VectorStoreService 获取集合统计
    stats = indexer._status_store._vectorstore.get_collection_stats(project_id)  # type: ignore[attr-defined]
    return create_response(
        data=stats,
        message=ResponseMessage.QUERY_SUCCESS,
        code=200,
    )

