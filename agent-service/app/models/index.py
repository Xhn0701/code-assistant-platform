"""
代码索引相关 API 模型。
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class IndexStatus(str, Enum):
    """索引状态枚举。"""

    PENDING = "PENDING"
    INDEXING = "INDEXING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IndexRepositoryRequest(BaseModel):
    """索引仓库请求体。"""

    project_id: int = Field(alias="projectId", description="项目 ID")
    repository_url: str = Field(alias="repositoryUrl", description="本地仓库路径")

    model_config = ConfigDict(populate_by_name=True)


class IndexRepositoryResult(BaseModel):
    """索引仓库结果。"""

    project_id: int = Field(alias="projectId", description="项目 ID")
    status: IndexStatus = Field(description="索引状态")
    total_files: int = Field(alias="totalFiles", description="扫描到的文件总数")
    indexed_files: int = Field(alias="indexedFiles", description="已索引的文件数")
    error_message: Optional[str] = Field(
        default=None, alias="errorMessage", description="失败原因（仅 FAILED 时有值）"
    )

    model_config = ConfigDict(populate_by_name=True)


class IndexStatusResponse(BaseModel):
    """索引状态查询结果。"""

    project_id: int = Field(alias="projectId", description="项目 ID")
    status: IndexStatus = Field(description="索引状态")
    total_files: int = Field(alias="totalFiles", description="扫描到的文件总数")
    indexed_files: int = Field(alias="indexedFiles", description="已索引的文件数")
    error_message: Optional[str] = Field(
        default=None, alias="errorMessage", description="失败原因（仅 FAILED 时有值）"
    )

    model_config = ConfigDict(populate_by_name=True)

