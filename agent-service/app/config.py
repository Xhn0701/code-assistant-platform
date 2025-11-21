"""
配置管理模块
使用 pydantic-settings 从环境变量加载配置
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置

    所有配置项都可以通过环境变量或 .env 文件进行设置。
    """

    # ========== 应用基本配置 ==========
    app_name: str = Field(default="Agent Service", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    app_description: str = Field(default="智能代码助手 - Agent 服务", description="应用描述")
    debug: bool = Field(default=False, description="调试模式")

    # ========== 服务器配置 ==========
    host: str = Field(default="0.0.0.0", description="监听地址")
    port: int = Field(default=8000, description="监听端口")
    workers: int = Field(default=1, description="Worker 进程数")

    # ========== CORS 配置 ==========
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="允许的 CORS 源（逗号分隔）",
    )

    # ========== Redis 配置 ==========
    redis_host: str = Field(default="localhost", description="Redis 主机")
    redis_port: int = Field(default=6379, description="Redis 端口")
    redis_password: Optional[str] = Field(default=None, description="Redis 密码")
    redis_db: int = Field(default=1, description="Redis 数据库编号（0 留给 Java 服务）")
    redis_timeout: int = Field(default=3, description="Redis 连接超时（秒）")

    # ========== OpenAI 配置 ==========
    openai_api_key: str = Field(default="", description="OpenAI API 密钥")
    openai_api_base: Optional[str] = Field(
        default=None,
        description="OpenAI API 基础 URL（可选，用于代理或自建服务）",
    )
    openai_model: str = Field(default="gpt-4o-mini", description="对话使用的模型")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding 模型（用于向量检索）",
    )
    openai_temperature: float = Field(default=0.7, description="Temperature 参数")
    openai_max_tokens: int = Field(default=2000, description="最大生成 tokens 数")

    # ========== ChromaDB 配置 ==========
    chroma_persist_directory: str = Field(
        default="./data/chroma",
        description="ChromaDB 持久化目录",
    )
    chroma_collection_name: str = Field(
        default="code_embeddings",
        description="默认集合名称前缀",
    )

    # ========== 代码索引配置 ==========
    index_batch_size: int = Field(default=100, description="批量索引大小")
    index_chunk_size: int = Field(default=1000, description="文本分块大小")
    index_chunk_overlap: int = Field(default=200, description="文本分块重叠大小")
    index_max_file_size: int = Field(
        default=1048576,  # 1MB
        description="索引的最大文件大小（字节）",
    )

    # ========== Java 服务配置 ==========
    java_user_service_url: str = Field(
        default="http://localhost:8080",
        description="Java 用户服务 URL",
    )

    # ========== 日志配置 ==========
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(
        default="json",
        description="日志格式（json 或 text）",
    )

    # ========== 速率限制配置 ==========
    rate_limit_enabled: bool = Field(default=True, description="是否启用速率限制")
    rate_limit_requests: int = Field(default=100, description="每分钟最大请求数")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 忽略环境变量中的额外字段
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """返回 CORS 源列表"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def redis_url(self) -> str:
        """返回 Redis 连接 URL"""
        if self.redis_password:
            return (
                f"redis://:{self.redis_password}@{self.redis_host}:"
                f"{self.redis_port}/{self.redis_db}"
            )
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    使用 lru_cache 确保配置只加载一次
    """
    return Settings()


# 便捷导出
settings = get_settings()

