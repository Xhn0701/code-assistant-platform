"""
Code Review 异步任务
"""
import asyncio
import logging
from typing import List, Optional

from app.core.celery_app import celery_app
from app.agents.review_agent import ReviewAgent

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def review_code_task(
    self,
    project_id: int,
    project_path: str,
    files: Optional[List[str]] = None,
    level: str = "standard"
):
    """
    异步执行代码审查

    Args:
        project_id: 项目ID
        project_path: 项目路径
        files: 指定文件列表
        level: 审查深度 (quick/standard/full)
    """
    try:
        # 更新进度: 10%
        self.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'message': '正在初始化审查环境...'}
        )

        # 创建 ReviewAgent
        agent = ReviewAgent()

        # 更新进度: 30%
        self.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'message': '正在执行静态分析...'}
        )

        # 执行审查 (异步)
        report = asyncio.run(agent.review_code(
            project_id=project_id,
            project_path=project_path,
            files=files,
            level=level
        ))

        # 更新进度: 90%
        self.update_state(
            state='PROGRESS',
            meta={'progress': 90, 'message': '正在生成报告...'}
        )

        # 返回报告 (会自动变为SUCCESS状态)
        return report.to_dict()

    except Exception as e:
        logger.error(f"代码审查失败: {e}", exc_info=True)
        # 失败时会自动变为FAILURE状态
        raise
