"""
Tasks API - 任务状态查询
"""
from fastapi import APIRouter
from celery.result import AsyncResult

from app.core.response import ResponseModel

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    查询Celery任务状态

    Returns:
        {
            "state": "PENDING|PROGRESS|SUCCESS|FAILURE",
            "progress": 0-100,
            "message": "当前进度描述",
            "result": {...},  # 任务结果(SUCCESS时)
            "error": "错误信息"  # 失败原因(FAILURE时)
        }
    """
    try:
        result = AsyncResult(task_id)

        response_data = {
            "state": result.state,
            "progress": 0,
            "message": ""
        }

        if result.state == 'PENDING':
            response_data['message'] = '任务排队中...'

        elif result.state == 'PROGRESS':
            # 获取进度信息 (在任务中通过update_state设置)
            info = result.info or {}
            response_data['progress'] = info.get('progress', 0)
            response_data['message'] = info.get('message', '处理中...')

        elif result.state == 'SUCCESS':
            response_data['progress'] = 100
            response_data['message'] = '任务完成'
            response_data['result'] = result.result

        elif result.state == 'FAILURE':
            response_data['message'] = '任务失败'
            response_data['error'] = str(result.info)

        return ResponseModel.ok(data=response_data)

    except Exception as e:
        return ResponseModel.fail(
            code=5003,
            message=f"查询任务状态失败: {str(e)}"
        )
