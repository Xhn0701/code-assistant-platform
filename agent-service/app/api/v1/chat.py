"""
代码问答相关 API。
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, status

from app.core.exceptions import AgentErrorCode, AgentException
from app.core.response import ResponseMessage, ResponseModel, create_error_response, create_response
from app.dependencies import get_code_indexer, get_qa_agent
from app.models.chat import ChatAskRequest, ChatAskResponse
from app.models.index import IndexStatus
from app.services.code_indexer import CodeIndexer
from app.agents.qa_agent import QaAgent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/ask",
    response_model=ResponseModel[ChatAskResponse],
    status_code=status.HTTP_200_OK,
    summary="代码问答（RAG）",
    description="基于已建立的代码索引，回答关于指定项目代码的问题。",
)
async def ask_code_question(
    body: ChatAskRequest,
    indexer: CodeIndexer = Depends(get_code_indexer),
    qa_agent: QaAgent = Depends(get_qa_agent),
) -> ResponseModel[ChatAskResponse]:
    """
    代码问答主接口。

    前置条件：
    - 对应项目的代码索引已完成（COMPLETED）
    """
    # 检查索引状态
    status_obj = indexer.get_index_status(body.project_id)
    if status_obj.status != IndexStatus.COMPLETED:
        raise AgentException(
            AgentErrorCode.INDEX_NOT_READY,
            "代码索引未完成，请稍后再试",
        )

    # 调用 QA Agent 执行问答
    answer = await qa_agent.ask(body.project_id, body.question)
    response = ChatAskResponse(
        answer=answer.answer,
        sources=answer.sources,
        conversation_id=body.conversation_id,
    )
    return create_response(
        data=response,
        message=ResponseMessage.QUERY_SUCCESS,
        code=200,
    )


@router.post(
    "",
    response_model=ResponseModel[ChatAskResponse],
    status_code=status.HTTP_200_OK,
    summary="代码问答（兼容旧版前端）",
    description="兼容 web-client 当前使用的 /api/v1/chat 接口，内部转发到 /chat/ask。",
)
async def chat_compat(
    payload: Dict[str, Any],
    indexer: CodeIndexer = Depends(get_code_indexer),
    qa_agent: QaAgent = Depends(get_qa_agent),
) -> ResponseModel[ChatAskResponse]:
    """
    兼容 web-client 现有实现：
    - 请求体字段为 project_id / message
    """
    project_id = payload.get("project_id") or payload.get("projectId")
    message = payload.get("message") or payload.get("question")

    if not isinstance(project_id, int) or not isinstance(message, str):
        raise AgentException(
            AgentErrorCode.PARAM_ERROR,
            "请求参数错误，应包含整数 project_id 和字符串 message",
            data={"received": payload},
        )

    # 复用主逻辑
    request_model = ChatAskRequest(projectId=project_id, question=message)
    return await ask_code_question(
        body=request_model,
        indexer=indexer,
        qa_agent=qa_agent,
    )

