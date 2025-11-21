"""
智能代码助手平台 - Python Agent 服务入口

提供基于 LangChain 的 RAG 问答和代码审查 Agent 功能。
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pythonjsonlogger import jsonlogger

from app.api.v1 import api_router
from app.config import settings
from app.core.exceptions import AgentException
from app.core.response import create_error_response
from app.services.vectorstore import init_chroma_client, cleanup_chroma_client


# ========== 日志配置 ==========


def setup_logging() -> logging.Logger:
    """配置日志系统。"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # 清除现有 handlers
    logger.handlers.clear()

    # 创建 handler
    handler = logging.StreamHandler(sys.stdout)

    # 根据配置选择日志格式
    if settings.log_format == "json":
        # JSON 格式日志（生产环境推荐）
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # 文本格式日志（开发环境推荐）
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logging()


# ========== 应用生命周期 ==========


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理。

    启动时：
    - 打印启动信息
    - 初始化向量数据库客户端

    关闭时：
    - 清理资源
    """

    # 启动日志
    logger.info("=" * 60)
    logger.info("🚀 %s v%s 启动中...", settings.app_name, settings.app_version)
    logger.info("📝 调试模式: %s", settings.debug)
    logger.info("🔗 监听地址: http://%s:%s", settings.host, settings.port)
    logger.info("📚 API 文档: http://%s:%s/docs", settings.host, settings.port)
    logger.info("🔍 健康检查: http://%s:%s/api/v1/health", settings.host, settings.port)
    logger.info("=" * 60)

    # 初始化向量数据库客户端
    init_chroma_client()

    # TODO: 后续可在这里预加载本地模型等资源

    yield  # 应用运行期间

    # 关闭阶段
    logger.info("👋 %s 正在关闭...", settings.app_name)
    cleanup_chroma_client()


# ========== 创建 FastAPI 应用 ==========

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ========== 中间件配置 ==========

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 全局异常处理 ==========


@app.exception_handler(AgentException)
async def agent_exception_handler(request: Request, exc: AgentException):
    """
    处理业务异常。
    """
    logger.warning(
        "业务异常: %s",
        exc.message,
        extra={
            "error_code": exc.error_code.value,
            "path": request.url.path,
            "data": exc.data,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # 业务异常返回 200，由 code 字段区分
        content=create_error_response(
            message=exc.message,
            code=exc.error_code.value,
            data=exc.data,
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理参数验证异常。
    """
    logger.warning(
        "参数验证失败: %s",
        exc.errors(),
        extra={"path": request.url.path},
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=create_error_response(
            message="参数验证失败",
            code=1000,  # PARAM_ERROR
            data={"errors": exc.errors()},
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    处理未捕获的异常。
    """
    logger.error(
        "未捕获异常: %s",
        exc,
        exc_info=True,
        extra={"path": request.url.path},
    )
    message = "服务器内部错误" if not settings.debug else str(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            message=message,
            code=1001,  # INTERNAL_ERROR
        ).model_dump(),
    )


# ========== 注册路由 ==========

# 注册 v1 版本 API 路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    """根路径 - 返回服务信息。"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# ========== 启动入口 ==========

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,  # 开发模式下启用热重载
        workers=1 if settings.debug else settings.workers,
        log_level=settings.log_level.lower(),
        access_log=True,
    )

