"""
VectorStoreService 单元测试

测试向量存储服务的功能：
- Chroma 客户端初始化
- 集合管理（创建、重置、删除）
- 文档批量写入
- 检索器构造
- 集合统计
"""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.core.exceptions import AgentException, AgentErrorCode
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore import (
    VectorStoreService,
    cleanup_chroma_client,
    get_chroma_client,
    init_chroma_client,
)


class FakeEmbeddings(Embeddings):
    """
    用于测试的假 Embedding 实现。

    生成固定长度的随机向量，避免依赖真实 OpenAI API。
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """为文档列表生成假向量"""
        return [[0.1] * 1536 for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        """为查询生成假向量"""
        return [0.1] * 1536


@pytest.fixture
def fake_embedding_service():
    """提供使用假 Embedding 的服务"""
    service = MagicMock(spec=EmbeddingService)
    service.embedding = FakeEmbeddings()
    return service


class TestChromaClientManagement:
    """测试 Chroma 客户端的生命周期管理"""

    def test_init_chroma_client(self, temp_chroma_dir: str):
        """测试初始化 Chroma 客户端"""
        cleanup_chroma_client()  # 清理可能的旧客户端

        init_chroma_client()
        client = get_chroma_client()

        assert client is not None
        assert client._identifier is not None  # Chroma 客户端内部字段

    def test_init_chroma_client_idempotent(self, temp_chroma_dir: str):
        """测试重复初始化是幂等的"""
        cleanup_chroma_client()

        init_chroma_client()
        client1 = get_chroma_client()

        init_chroma_client()  # 第二次初始化
        client2 = get_chroma_client()

        # 应该返回同一个客户端实例
        assert client1 is client2

    def test_get_chroma_client_without_init(self):
        """测试未初始化时获取客户端应抛出异常"""
        cleanup_chroma_client()

        with pytest.raises(RuntimeError, match="ChromaDB 客户端未初始化"):
            get_chroma_client()

    def test_cleanup_chroma_client(self, temp_chroma_dir: str):
        """测试清理 Chroma 客户端"""
        init_chroma_client()
        assert get_chroma_client() is not None

        cleanup_chroma_client()

        with pytest.raises(RuntimeError):
            get_chroma_client()


class TestVectorStoreService:
    """VectorStoreService 测试套件"""

    @pytest.fixture(autouse=True)
    def setup_chroma(self, temp_chroma_dir: str):
        """每个测试前初始化 Chroma 客户端"""
        cleanup_chroma_client()
        init_chroma_client()
        yield
        cleanup_chroma_client()

    def test_collection_name_generation(self, fake_embedding_service):
        """测试集合名称生成规则"""
        service = VectorStoreService(fake_embedding_service)

        name1 = service._collection_name(1)
        name2 = service._collection_name(999)

        assert "project_1" in name1
        assert "project_999" in name2
        assert name1 != name2

    def test_reset_collection_creates_new(self, fake_embedding_service):
        """测试重置集合会创建新集合"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        # 重置集合
        service.reset_collection(project_id)

        # 验证集合已创建
        stats = service.get_collection_stats(project_id)
        assert stats["doc_count"] == 0

    def test_reset_collection_deletes_old_data(self, fake_embedding_service):
        """测试重置集合会删除旧数据"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        # 创建集合并写入文档
        service.reset_collection(project_id)
        docs = [Document(page_content="test", metadata={"source": "test"})]
        service.upsert_documents_batch(project_id, docs)

        # 验证有数据
        stats_before = service.get_collection_stats(project_id)
        assert stats_before["doc_count"] == 1

        # 重置集合
        service.reset_collection(project_id)

        # 验证数据被清空
        stats_after = service.get_collection_stats(project_id)
        assert stats_after["doc_count"] == 0

    def test_upsert_documents_batch_success(self, fake_embedding_service):
        """测试批量写入文档成功"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)

        # 写入文档
        docs = [
            Document(page_content="public class User {}", metadata={"path": "User.java"}),
            Document(
                page_content="public class Order {}", metadata={"path": "Order.java"}
            ),
        ]
        service.upsert_documents_batch(project_id, docs)

        # 验证文档数
        stats = service.get_collection_stats(project_id)
        assert stats["doc_count"] == 2

    def test_upsert_empty_documents_list(self, fake_embedding_service):
        """测试写入空文档列表"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)
        service.upsert_documents_batch(project_id, [])  # 空列表

        stats = service.get_collection_stats(project_id)
        assert stats["doc_count"] == 0

    def test_get_retriever_returns_valid_retriever(self, fake_embedding_service):
        """测试获取检索器返回有效对象"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)

        # 写入测试数据
        docs = [
            Document(page_content="authentication logic", metadata={"path": "Auth.java"})
        ]
        service.upsert_documents_batch(project_id, docs)

        # 获取 Retriever
        retriever = service.get_retriever(project_id, k=5)

        assert retriever is not None
        # 验证 Retriever 可以调用
        results = retriever.invoke("authentication")
        assert isinstance(results, list)

    def test_get_retriever_with_custom_k(self, fake_embedding_service):
        """测试自定义检索数量 k"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)

        # 写入多个文档
        docs = [
            Document(page_content=f"Document {i}", metadata={"index": i})
            for i in range(10)
        ]
        service.upsert_documents_batch(project_id, docs)

        # 测试不同的 k 值
        retriever_k3 = service.get_retriever(project_id, k=3)
        retriever_k5 = service.get_retriever(project_id, k=5)

        # 验证检索器对象不同
        assert retriever_k3 is not retriever_k5

    def test_get_collection_stats_for_existing_collection(self, fake_embedding_service):
        """测试获取已存在集合的统计信息"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)

        # 写入 5 个文档
        docs = [Document(page_content=f"doc{i}") for i in range(5)]
        service.upsert_documents_batch(project_id, docs)

        stats = service.get_collection_stats(project_id)

        assert stats["doc_count"] == 5
        assert "project_1" in stats["name"]

    def test_get_collection_stats_for_nonexistent_collection(self, fake_embedding_service):
        """测试获取不存在集合的统计信息（应返回 0）"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 9999  # 未创建的项目

        stats = service.get_collection_stats(project_id)

        assert stats["doc_count"] == 0
        assert "project_9999" in stats["name"]

    def test_multiple_projects_isolation(self, fake_embedding_service):
        """测试不同项目的数据隔离"""
        service = VectorStoreService(fake_embedding_service)

        # 项目 1: 写入 3 个文档
        service.reset_collection(1)
        docs1 = [Document(page_content=f"project1_doc{i}") for i in range(3)]
        service.upsert_documents_batch(1, docs1)

        # 项目 2: 写入 5 个文档
        service.reset_collection(2)
        docs2 = [Document(page_content=f"project2_doc{i}") for i in range(5)]
        service.upsert_documents_batch(2, docs2)

        # 验证各自的文档数
        stats1 = service.get_collection_stats(1)
        stats2 = service.get_collection_stats(2)

        assert stats1["doc_count"] == 3
        assert stats2["doc_count"] == 5

    def test_batch_upsert_large_documents(self, fake_embedding_service):
        """测试批量写入大量文档"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)

        # 创建 100 个文档
        docs = [
            Document(
                page_content=f"public class Class{i} {{ /* code */ }}",
                metadata={"path": f"Class{i}.java", "index": i},
            )
            for i in range(100)
        ]

        service.upsert_documents_batch(project_id, docs)

        stats = service.get_collection_stats(project_id)
        assert stats["doc_count"] == 100

    def test_document_metadata_preservation(self, fake_embedding_service):
        """测试文档元数据的保留"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)

        # 写入带详细元数据的文档
        docs = [
            Document(
                page_content="authentication code",
                metadata={
                    "path": "Auth.java",
                    "language": "java",
                    "start_line": 10,
                    "end_line": 50,
                },
            )
        ]
        service.upsert_documents_batch(project_id, docs)

        # 通过检索器获取文档
        retriever = service.get_retriever(project_id)
        results = retriever.invoke("authentication")

        # 验证元数据完整性
        assert len(results) > 0
        assert results[0].metadata["path"] == "Auth.java"
        assert results[0].metadata["language"] == "java"
        assert results[0].metadata["start_line"] == 10
        assert results[0].metadata["end_line"] == 50

    def test_incremental_upsert(self, fake_embedding_service):
        """测试增量写入文档"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)

        # 第一次写入 3 个文档
        docs1 = [Document(page_content=f"doc{i}") for i in range(3)]
        service.upsert_documents_batch(project_id, docs1)

        assert service.get_collection_stats(project_id)["doc_count"] == 3

        # 第二次写入 2 个文档
        docs2 = [Document(page_content=f"doc{i}") for i in range(3, 5)]
        service.upsert_documents_batch(project_id, docs2)

        assert service.get_collection_stats(project_id)["doc_count"] == 5

    def test_retriever_semantic_search(self, fake_embedding_service):
        """测试检索器的语义搜索（使用假 Embedding）"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)

        # 写入不同主题的文档
        docs = [
            Document(
                page_content="User authentication with JWT token",
                metadata={"path": "Auth.java"},
            ),
            Document(
                page_content="Database connection pooling",
                metadata={"path": "DB.java"},
            ),
            Document(
                page_content="User login and registration",
                metadata={"path": "User.java"},
            ),
        ]
        service.upsert_documents_batch(project_id, docs)

        # 检索相关文档
        retriever = service.get_retriever(project_id, k=2)
        results = retriever.invoke("user authentication")

        # 验证返回结果
        assert len(results) <= 2  # k=2
        assert all(isinstance(doc, Document) for doc in results)

    def test_collection_name_includes_settings_prefix(self, fake_embedding_service):
        """验证集合名称包含配置的前缀"""
        from app.config import settings

        service = VectorStoreService(fake_embedding_service)
        name = service._collection_name(1)

        assert settings.chroma_collection_name in name
        assert "project_1" in name

    def test_upsert_with_duplicate_content(self, fake_embedding_service):
        """测试写入重复内容的文档"""
        service = VectorStoreService(fake_embedding_service)
        project_id = 1

        service.reset_collection(project_id)

        # 写入两个内容相同的文档
        docs = [
            Document(page_content="duplicate content", metadata={"id": "1"}),
            Document(page_content="duplicate content", metadata={"id": "2"}),
        ]
        service.upsert_documents_batch(project_id, docs)

        # 应该有 2 个文档（即使内容重复）
        stats = service.get_collection_stats(project_id)
        assert stats["doc_count"] == 2
