"""
EmbeddingService 单元测试

测试 Embedding 服务的功能：
- 服务初始化
- 文档向量生成
- 查询向量生成
- 错误处理和重试机制
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import AgentException, AgentErrorCode
from app.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """EmbeddingService 测试套件"""

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_initialization_success(self, mock_openai_embeddings, test_settings):
        """测试成功初始化 Embedding 服务"""
        # Mock OpenAIEmbeddings 构造函数
        mock_instance = MagicMock()
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()

        # 验证 OpenAIEmbeddings 被正确调用
        mock_openai_embeddings.assert_called_once()
        call_kwargs = mock_openai_embeddings.call_args.kwargs

        assert call_kwargs["model"] == test_settings.openai_embedding_model
        assert service.embedding is not None

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_initialization_failure(self, mock_openai_embeddings, test_settings):
        """测试初始化失败时抛出异常"""
        # Mock 抛出异常
        mock_openai_embeddings.side_effect = Exception("API key invalid")

        with pytest.raises(AgentException) as exc_info:
            EmbeddingService()

        assert exc_info.value.error_code == AgentErrorCode.OPENAI_API_ERROR
        assert "初始化 Embedding 客户端失败" in exc_info.value.message

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_documents_success(self, mock_openai_embeddings):
        """测试批量生成文档向量成功"""
        # Mock embed_documents 方法
        mock_instance = MagicMock()
        mock_instance.embed_documents.return_value = [
            [0.1] * 1536,  # 第一个文档的向量
            [0.2] * 1536,  # 第二个文档的向量
        ]
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        texts = ["public class User {}", "public class Order {}"]

        vectors = service.embed_documents(texts)

        # 验证返回结果
        assert len(vectors) == 2
        assert len(vectors[0]) == 1536
        assert len(vectors[1]) == 1536

        # 验证调用参数
        mock_instance.embed_documents.assert_called_once_with(texts)

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_documents_empty_list(self, mock_openai_embeddings):
        """测试空文档列表"""
        mock_instance = MagicMock()
        mock_instance.embed_documents.return_value = []
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        vectors = service.embed_documents([])

        assert vectors == []

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_documents_single_document(self, mock_openai_embeddings):
        """测试单个文档向量生成"""
        mock_instance = MagicMock()
        mock_instance.embed_documents.return_value = [[0.3] * 1536]
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        vectors = service.embed_documents(["single document"])

        assert len(vectors) == 1
        assert len(vectors[0]) == 1536

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_query_success(self, mock_openai_embeddings):
        """测试查询向量生成成功"""
        mock_instance = MagicMock()
        mock_instance.embed_query.return_value = [0.5] * 1536
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        vector = service.embed_query("how to authenticate user?")

        # 验证返回结果
        assert len(vector) == 1536
        assert all(v == 0.5 for v in vector)

        # 验证调用参数
        mock_instance.embed_query.assert_called_once_with("how to authenticate user?")

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_query_chinese_text(self, mock_openai_embeddings):
        """测试中文查询向量生成"""
        mock_instance = MagicMock()
        mock_instance.embed_query.return_value = [0.6] * 1536
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        vector = service.embed_query("如何实现用户认证？")

        assert len(vector) == 1536
        mock_instance.embed_query.assert_called_once_with("如何实现用户认证？")

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_documents_with_retry_on_failure(self, mock_openai_embeddings):
        """测试文档向量生成失败时的重试机制"""
        mock_instance = MagicMock()

        # 第一次调用失败，第二次成功
        mock_instance.embed_documents.side_effect = [
            Exception("Rate limit exceeded"),  # 第一次失败
            [[0.1] * 1536],  # 第二次成功
        ]
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        vectors = service.embed_documents(["test"])

        # 应该成功（经过重试）
        assert len(vectors) == 1
        assert mock_instance.embed_documents.call_count == 2

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_documents_max_retries_exceeded(self, mock_openai_embeddings):
        """测试重试次数耗尽后抛出异常"""
        from tenacity import RetryError

        mock_instance = MagicMock()

        # 所有重试都失败（3 次尝试）
        mock_instance.embed_documents.side_effect = Exception("Persistent error")
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()

        # retry 装饰器会将异常包装成 RetryError
        with pytest.raises(RetryError) as exc_info:
            service.embed_documents(["test"])

        # 验证内部的原始异常是 AgentException
        original_exc = exc_info.value.last_attempt.exception()
        assert isinstance(original_exc, AgentException)
        assert original_exc.error_code == AgentErrorCode.EMBEDDING_ERROR

        # 验证重试了 3 次
        assert mock_instance.embed_documents.call_count == 3

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_query_with_retry_on_failure(self, mock_openai_embeddings):
        """测试查询向量生成失败时的重试机制"""
        mock_instance = MagicMock()

        # 第一次失败，第二次成功
        mock_instance.embed_query.side_effect = [
            Exception("Network error"),
            [0.7] * 1536,
        ]
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        vector = service.embed_query("test query")

        assert len(vector) == 1536
        assert mock_instance.embed_query.call_count == 2

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_query_max_retries_exceeded(self, mock_openai_embeddings):
        """测试查询向量重试次数耗尽"""
        from tenacity import RetryError

        mock_instance = MagicMock()
        mock_instance.embed_query.side_effect = Exception("Persistent query error")
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()

        # retry 装饰器会将异常包装成 RetryError
        with pytest.raises(RetryError) as exc_info:
            service.embed_query("test query")

        # 验证内部的原始异常是 AgentException
        original_exc = exc_info.value.last_attempt.exception()
        assert isinstance(original_exc, AgentException)
        assert original_exc.error_code == AgentErrorCode.EMBEDDING_ERROR

        assert mock_instance.embed_query.call_count == 3

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embedding_property_returns_underlying_object(self, mock_openai_embeddings):
        """测试 embedding 属性返回底层 OpenAIEmbeddings 对象"""
        mock_instance = MagicMock()
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()

        assert service.embedding is mock_instance

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_large_batch_documents(self, mock_openai_embeddings):
        """测试大批量文档向量生成"""
        mock_instance = MagicMock()

        # 生成 100 个文档的向量
        mock_instance.embed_documents.return_value = [[0.1] * 1536 for _ in range(100)]
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        texts = [f"document {i}" for i in range(100)]
        vectors = service.embed_documents(texts)

        assert len(vectors) == 100
        assert all(len(v) == 1536 for v in vectors)

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_documents_with_special_characters(self, mock_openai_embeddings):
        """测试包含特殊字符的文档"""
        mock_instance = MagicMock()
        mock_instance.embed_documents.return_value = [[0.2] * 1536]
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        texts = ["public class User { /* 中文注释 */ @Override toString() {} }"]
        vectors = service.embed_documents(texts)

        assert len(vectors) == 1
        mock_instance.embed_documents.assert_called_once_with(texts)

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_embed_query_with_multiline_text(self, mock_openai_embeddings):
        """测试多行查询文本"""
        mock_instance = MagicMock()
        mock_instance.embed_query.return_value = [0.3] * 1536
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()
        query = """
        How to implement user authentication?
        Should I use JWT or Session?
        """
        vector = service.embed_query(query)

        assert len(vector) == 1536
        mock_instance.embed_query.assert_called_once_with(query)

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    @patch("app.services.embedding_service.settings")
    def test_uses_configured_model(self, mock_settings, mock_openai_embeddings):
        """测试使用配置的模型"""
        mock_settings.openai_embedding_model = "text-embedding-3-large"
        mock_settings.openai_api_key = "sk-test-key"
        mock_settings.openai_api_base = None

        mock_instance = MagicMock()
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()

        # 验证使用了配置的模型
        call_kwargs = mock_openai_embeddings.call_args.kwargs
        assert call_kwargs["model"] == "text-embedding-3-large"

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    @patch("app.services.embedding_service.settings")
    def test_uses_custom_api_base(self, mock_settings, mock_openai_embeddings):
        """测试使用自定义 API Base URL"""
        mock_settings.openai_embedding_model = "text-embedding-3-small"
        mock_settings.openai_api_key = "sk-test-key"
        mock_settings.openai_api_base = "https://custom.openai.proxy.com/v1"

        mock_instance = MagicMock()
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()

        call_kwargs = mock_openai_embeddings.call_args.kwargs
        assert call_kwargs["base_url"] == "https://custom.openai.proxy.com/v1"

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    def test_concurrent_embed_calls(self, mock_openai_embeddings):
        """测试并发调用 embed 方法"""
        mock_instance = MagicMock()
        mock_instance.embed_documents.return_value = [[0.1] * 1536]
        mock_instance.embed_query.return_value = [0.2] * 1536
        mock_openai_embeddings.return_value = mock_instance

        service = EmbeddingService()

        # 多次调用
        service.embed_documents(["doc1"])
        service.embed_query("query1")
        service.embed_documents(["doc2", "doc3"])

        # 验证调用次数
        assert mock_instance.embed_documents.call_count == 2
        assert mock_instance.embed_query.call_count == 1
