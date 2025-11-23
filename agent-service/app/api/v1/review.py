"""
Code Review API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from celery.result import AsyncResult

from app.core.response import ResponseModel
from app.tasks.review_tasks import review_code_task

router = APIRouter(prefix="/review", tags=["review"])


class ReviewRequest(BaseModel):
    """代码审查请求"""
    projectId: int = Field(..., description="项目ID")
    projectPath: str = Field(..., description="项目路径")
    files: Optional[List[str]] = Field(None, description="指定文件列表,为空则全量审查")
    level: str = Field("standard", description="审查深度: quick/standard/full")


class ReviewTaskResponse(BaseModel):
    """审查任务响应"""
    taskId: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    estimatedTime: int = Field(..., description="预估耗时(秒)")


@router.post("/analyze", response_model=ResponseModel[ReviewTaskResponse])
async def submit_review_task(request: ReviewRequest):
    """
    提交代码审查任务

    创建异步审查任务并返回任务ID
    """
    try:
        # 创建异步任务
        task = review_code_task.delay(
            project_id=request.projectId,
            project_path=request.projectPath,
            files=request.files,
            level=request.level
        )

        # 预估时间 (根据审查级别)
        estimated_time = _estimate_review_time(request.level)

        return ResponseModel.ok(
            data=ReviewTaskResponse(
                taskId=task.id,
                status="PENDING",
                estimatedTime=estimated_time
            )
        )

    except Exception as e:
        return ResponseModel.fail(
            code=5001,
            message=f"创建审查任务失败: {str(e)}"
        )


@router.get("/result/{task_id}")
async def get_review_result(task_id: str):
    """
    查询审查结果

    根据任务状态返回不同响应:
    - PENDING: 排队中
    - PROGRESS: 进行中 (返回进度)
    - SUCCESS: 完成 (返回报告)
    - FAILURE: 失败 (返回错误)
    """
    try:
        result = AsyncResult(task_id)

        if result.state == 'PENDING':
            return ResponseModel.fail(
                code=3001,
                message="审查任务排队中",
                data={"progress": 0, "state": "PENDING"}
            )

        if result.state == 'PROGRESS':
            return ResponseModel.fail(
                code=3002,
                message="审查任务进行中",
                data=result.info
            )

        if result.state == 'FAILURE':
            return ResponseModel.fail(
                code=3003,
                message="审查任务失败",
                data={"error": str(result.info)}
            )

        # SUCCESS
        report = result.result
        return ResponseModel.ok(data=report)

    except Exception as e:
        return ResponseModel.fail(
            code=5002,
            message=f"查询审查结果失败: {str(e)}"
        )


def _estimate_review_time(level: str) -> int:
    """预估审查耗时 (秒)"""
    time_map = {
        'quick': 30,
        'standard': 60,
        'full': 120
    }
    return time_map.get(level, 60)
