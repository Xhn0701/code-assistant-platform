# Celery tasks package
# 导入所有任务,以便Celery可以发现它们
from app.tasks.review_tasks import review_code_task

__all__ = ['review_code_task']
