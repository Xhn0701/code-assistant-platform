"""
RAG 问答 Agent 实现。
"""

import logging
from typing import List

from langchain_openai import ChatOpenAI

from app.config import settings
from app.core.exceptions import AgentErrorCode, AgentException
from app.models.chat import AgentAnswer, ChatAskRequest, Source
from app.services.vectorstore import VectorStoreService

logger = logging.getLogger(__name__)


class QaAgent:
    """
    基于向量检索的代码问答 Agent。

    当前实现为无状态 RAG：仅基于当前问题和检索到的代码片段生成回答，
    对话历史由上层（Java 服务）管理并在后续版本接入。
    """

    def __init__(self, vectorstore: VectorStoreService) -> None:
        self._vectorstore = vectorstore
        try:
            self._llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key or None,
                base_url=settings.openai_api_base or None,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
            )
        except Exception as exc:  # pragma: no cover - 初始化异常较少发生
            logger.error("初始化 ChatOpenAI 失败: %s", exc, exc_info=True)
            raise AgentException(
                AgentErrorCode.OPENAI_API_ERROR,
                "初始化 LLM 客户端失败",
                data={"error": str(exc)},
            ) from exc

    async def ask(self, project_id: int, question: str) -> AgentAnswer:
        """针对指定项目执行一次 RAG 问答。"""
        logger.info("[项目 %s] 开始 RAG 问答: %s", project_id, question)

        # 1. 构造检索器并检索相关代码片段
        try:
            retriever = self._vectorstore.get_retriever(project_id, k=8)
            # BaseRetriever 在 langchain-core 0.1.46 后推荐使用 invoke 接口
            docs = retriever.invoke(question)
        except AgentException:
            raise
        except Exception as exc:
            logger.error("检索相关文档失败: %s", exc, exc_info=True)
            raise AgentException(
                AgentErrorCode.VECTOR_STORE_ERROR,
                "检索相关代码片段失败",
                data={"error": str(exc)},
            ) from exc

        if not docs:
            logger.info("[项目 %s] 未检索到相关代码片段，执行普通回答", project_id)
            context_text = "（未检索到相关代码片段，仅基于问题本身进行回答）"
            sources: List[Source] = []
        else:
            # 拼接上下文
            context_parts: List[str] = []
            sources = []
            for doc in docs:
                meta = doc.metadata or {}
                path = meta.get("path", "unknown")
                start_line = int(meta.get("start_line", 1))
                end_line = int(meta.get("end_line", start_line))
                score = float(meta.get("score", 0.0)) if "score" in meta else 0.0

                context_parts.append(
                    f"文件: {path} [{start_line}-{end_line}]\n{doc.page_content}"
                )
                sources.append(
                    Source(
                        file=path,
                        start_line=start_line,
                        end_line=end_line,
                        score=score,
                    )
                )

            context_text = "\n\n".join(context_parts)

        # 2. 构造提示词
        system_prompt = (
            "你是智能代码助手平台的代码助手，对项目代码结构非常熟悉。\n"
            "请基于给定的代码片段回答用户的问题，避免编造不存在的接口或模块。\n"
            "如果代码片段不足以回答，请明确说明“当前索引的代码不足以回答该问题”。"
        )
        user_prompt = (
            f"{system_prompt}\n\n"
            f"【用户问题】:\n{question}\n\n"
            f"【相关代码片段】:\n{context_text}\n\n"
            "请用简体中文给出详细回答，并在结尾简要列出你参考的文件列表。"
        )

        # 3. 调用 LLM 生成答案（异步）
        try:
            response = await self._llm.ainvoke(user_prompt)
            content = getattr(response, "content", None)
            answer_text = content if isinstance(content, str) else str(response)
        except Exception as exc:
            logger.error("调用 LLM 生成答案失败: %s", exc, exc_info=True)
            raise AgentException(
                AgentErrorCode.LLM_ERROR,
                "生成回答失败",
                data={"error": str(exc)},
            ) from exc

        return AgentAnswer(answer=answer_text, sources=sources, conversation_id=None)


__all__ = ["QaAgent"]
