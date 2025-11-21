"""
问答相关 API 模型�?"""

from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class Source(BaseModel):
    """答案引用的代码片段来源�?"""

    file: str = Field(description="文件路径（相对仓库根目录）")
    start_line: int = Field(
        alias="startLine",
        description="起始行号（近似）",
    )
    end_line: int = Field(
        alias="endLine",
        description="结束行号（近似）",
    )
    score: float = Field(description="相似度得分，范围 [0,1]，值越大越相关")

    # 允许使用字段名（start_line/end_line）进行赋值，同时对外序列化为驼峰命名
    model_config = ConfigDict(populate_by_name=True)


class ChatAskRequest(BaseModel):
    """代码问答请求体�?"""

    project_id: int = Field(alias="projectId", description="项目 ID")
    question: str = Field(description="用户问题")
    conversation_id: Optional[str] = Field(
        default=None,
        alias="conversationId",
        description="对话 ID（预留，用于后续多轮对话）",
    )

    model_config = ConfigDict(populate_by_name=True)


class ChatAskResponse(BaseModel):
    """代码问答响应体�?"""

    answer: str = Field(description="模型回答")
    sources: List[Source] = Field(description="参考的代码片段列表")
    conversation_id: Optional[str] = Field(
        default=None,
        alias="conversationId",
        description="对话 ID",
    )

    # 允许通过字段名 conversation_id 赋值，同时响应中使用 conversationId
    model_config = ConfigDict(populate_by_name=True)


class AgentAnswer(BaseModel):
    """
    Agent 内部使用的问答结果模型�?    �?ChatAskResponse 结构基本一致，但不强制别名�?    """

    answer: str
    sources: List[Source]
    conversation_id: Optional[str] = None
