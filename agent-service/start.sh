#!/bin/bash
# 启动脚本 - 同时启动 FastAPI 和 Celery worker

set -e

echo "Starting Agent Service..."

# 启动 Celery worker 在后台
echo "Starting Celery worker..."
celery -A app.core.celery_app.celery_app worker --loglevel=info --concurrency=2 &

# 等待2秒让worker启动
sleep 2

# 启动 FastAPI 应用
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
