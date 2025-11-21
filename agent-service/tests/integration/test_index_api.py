"""
索引 API 集成测试

测试端到端的索引流程：
- POST /api/v1/index/repository - 索引仓库
- GET /api/v1/index/status/{project_id} - 查询索引状态
- GET /api/v1/index/stats/{project_id} - 查询集合统计
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.core.response import ResponseMessage
from app.main import app


@pytest.mark.asyncio
class TestIndexRepositoryAPI:
    """测试索引仓库 API"""

    async def test_index_local_repository_success(self, sample_repository_path: Path):
        """测试成功索引本地仓库"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == ResponseMessage.INDEX_COMPLETED
        assert data["data"]["projectId"] == 1
        assert data["data"]["status"] == "COMPLETED"
        assert data["data"]["totalFiles"] > 0
        assert data["data"]["indexedFiles"] > 0

    async def test_index_nonexistent_repository(self):
        """测试索引不存在的仓库路径"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": "/nonexistent/path/to/repo",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 2000  # REPOSITORY_ERROR
        assert "仓库" in data["message"]

    async def test_index_repository_with_invalid_json(self):
        """测试无效的请求 JSON"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": "not_an_integer",  # 应该是整数
                    "repositoryUrl": "path",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1000  # PARAM_ERROR

    async def test_index_repository_missing_fields(self):
        """测试缺少必需字段"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    # 缺少 repositoryUrl
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1000  # PARAM_ERROR

    async def test_index_repository_twice_overwrites(
        self, sample_repository_path: Path
    ):
        """测试重复索引会覆盖旧数据"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 第一次索引
            response1 = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

            assert response1.status_code == 200
            data1 = response1.json()
            total_files1 = data1["data"]["totalFiles"]

            # 第二次索引（应覆盖）
            response2 = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

            assert response2.status_code == 200
            data2 = response2.json()
            # 文件数应该相同（因为是同一个仓库）
            assert data2["data"]["totalFiles"] == total_files1


@pytest.mark.asyncio
class TestIndexStatusAPI:
    """测试查询索引状态 API"""

    async def test_get_index_status_after_indexing(
        self, sample_repository_path: Path
    ):
        """测试索引完成后查询状态"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 先索引
            await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

            # 查询状态
            response = await client.get("/api/v1/index/status/1")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["projectId"] == 1
        assert data["data"]["status"] == "COMPLETED"
        assert data["data"]["totalFiles"] > 0

    async def test_get_index_status_not_found(self):
        """测试查询未索引项目的状态"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/index/status/9999")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 2002  # INDEX_NOT_READY

    async def test_get_index_status_invalid_project_id(self):
        """测试无效的 project_id 参数"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/index/status/invalid")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1000  # PARAM_ERROR


@pytest.mark.asyncio
class TestIndexStatsAPI:
    """测试查询索引统计 API"""

    async def test_get_index_stats_after_indexing(
        self, sample_repository_path: Path
    ):
        """测试索引后查询集合统计"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 先索引
            await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

            # 查询统计
            response = await client.get("/api/v1/index/stats/1")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "doc_count" in data["data"]
        assert data["data"]["doc_count"] > 0

    async def test_get_index_stats_for_nonexistent_project(self):
        """测试查询未索引项目的统计（应返回 0）"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/index/stats/9999")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["doc_count"] == 0


@pytest.mark.asyncio
class TestIndexAPIEndToEnd:
    """端到端测试完整索引流程"""

    async def test_full_index_workflow(self, sample_repository_path: Path):
        """测试完整的索引工作流"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            project_id = 1

            # 步骤 1: 索引仓库
            index_response = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": project_id,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

            assert index_response.status_code == 200
            index_data = index_response.json()
            assert index_data["data"]["status"] == "COMPLETED"

            total_files = index_data["data"]["totalFiles"]
            indexed_files = index_data["data"]["indexedFiles"]

            # 步骤 2: 查询索引状态（应该是 COMPLETED）
            status_response = await client.get(f"/api/v1/index/status/{project_id}")

            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["data"]["status"] == "COMPLETED"
            assert status_data["data"]["totalFiles"] == total_files
            assert status_data["data"]["indexedFiles"] == indexed_files

            # 步骤 3: 查询集合统计（文档数应 > 0）
            stats_response = await client.get(f"/api/v1/index/stats/{project_id}")

            assert stats_response.status_code == 200
            stats_data = stats_response.json()
            assert stats_data["data"]["doc_count"] > 0

    async def test_multiple_projects_isolated(self, sample_repository_path: Path):
        """测试多个项目的索引隔离"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 索引项目 1
            await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

            # 索引项目 2（相同仓库路径）
            await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 2,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

            # 查询各自状态
            status1 = await client.get("/api/v1/index/status/1")
            status2 = await client.get("/api/v1/index/status/2")

            assert status1.json()["data"]["projectId"] == 1
            assert status2.json()["data"]["projectId"] == 2

            # 查询各自统计
            stats1 = await client.get("/api/v1/index/stats/1")
            stats2 = await client.get("/api/v1/index/stats/2")

            # 两个项目都应有文档
            assert stats1.json()["data"]["doc_count"] > 0
            assert stats2.json()["data"]["doc_count"] > 0


@pytest.mark.asyncio
class TestIndexAPIWithMockedOpenAI:
    """测试使用 Mock OpenAI 的索引流程（避免实际 API 调用）"""

    @patch("app.services.embedding_service.OpenAIEmbeddings")
    async def test_index_with_mocked_embeddings(
        self, mock_openai_embeddings, sample_repository_path: Path
    ):
        """测试使用 Mock Embedding 的索引流程"""
        # Mock OpenAI Embeddings
        mock_instance = MagicMock()
        mock_instance.embed_documents.return_value = [[0.1] * 1536]
        mock_instance.embed_query.return_value = [0.1] * 1536
        mock_openai_embeddings.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

        # 验证索引成功
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "COMPLETED"

        # 验证 Mock 被调用
        assert mock_instance.embed_documents.called


@pytest.mark.asyncio
class TestIndexAPIResponseFormat:
    """测试 API 响应格式规范"""

    async def test_response_has_standard_structure(
        self, sample_repository_path: Path
    ):
        """验证响应符合标准结构"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": str(sample_repository_path),
                },
            )

        data = response.json()

        # 验证标准字段
        assert "code" in data
        assert "message" in data
        assert "data" in data
        assert isinstance(data["code"], int)
        assert isinstance(data["message"], str)
        assert isinstance(data["data"], dict)

    async def test_error_response_has_standard_structure(self):
        """验证错误响应符合标准结构"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/index/repository",
                json={
                    "projectId": 1,
                    "repositoryUrl": "/invalid/path",
                },
            )

        data = response.json()

        assert "code" in data
        assert "message" in data
        assert data["code"] != 0  # 错误码应非 0
