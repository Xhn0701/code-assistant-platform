"""
问答 API 集成测试

测试端到端的问答流程：
- POST /api/v1/chat/ask - RAG 问答
- POST /api/v1/chat - 兼容接口
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def indexed_project(sample_repository_path: Path) -> int:
    """创建已索引的项目（用于问答测试）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 先索引项目
        await client.post(
            "/api/v1/index/repository",
            json={
                "projectId": 1,
                "repositoryUrl": str(sample_repository_path),
            },
        )
    return 1  # 返回项目 ID


@pytest.mark.asyncio
class TestChatAskAPI:
    """测试代码问答 API"""

    @patch("app.agents.qa_agent.ChatOpenAI")
    async def test_ask_question_success(self, mock_chat_openai, indexed_project: int):
        """测试成功提问并获得答案"""
        # Mock OpenAI Chat 响应
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(
                content="This project uses Spring Security with JWT for authentication."
            )
        )
        mock_chat_openai.return_value = mock_llm

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": indexed_project,
                    "question": "How is authentication implemented?",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "查询成功"
        assert "answer" in data["data"]
        assert "sources" in data["data"]
        assert isinstance(data["data"]["sources"], list)

    async def test_ask_without_index(self):
        """测试对未索引项目提问（应返回错误）"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": 9999,  # 未索引的项目
                    "question": "What is this?",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 2002  # INDEX_NOT_READY
        assert "索引" in data["message"]

    async def test_ask_with_invalid_json(self):
        """测试无效的请求 JSON"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": "not_an_integer",
                    "question": "test",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1000  # PARAM_ERROR

    async def test_ask_missing_fields(self):
        """测试缺少必需字段"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": 1,
                    # 缺少 question
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1000  # PARAM_ERROR

    @patch("app.agents.qa_agent.ChatOpenAI")
    async def test_ask_chinese_question(self, mock_chat_openai, indexed_project: int):
        """测试中文提问"""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content="该项目使用 Spring Security 和 JWT 进行认证。")
        )
        mock_chat_openai.return_value = mock_llm

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": indexed_project,
                    "question": "认证逻辑是如何实现的？",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "answer" in data["data"]

    @patch("app.agents.qa_agent.ChatOpenAI")
    async def test_ask_with_conversation_id(
        self, mock_chat_openai, indexed_project: int
    ):
        """测试带会话 ID 的提问"""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content="Test answer")
        )
        mock_chat_openai.return_value = mock_llm

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": indexed_project,
                    "question": "test",
                    "conversationId": "conv-12345",
                },
            )

        assert response.status_code == 200
        data = response.json()
        # 当前实现会原样返回 conversationId
        assert data["data"]["conversationId"] == "conv-12345"


@pytest.mark.asyncio
class TestChatCompatAPI:
    """测试兼容接口"""

    @patch("app.agents.qa_agent.ChatOpenAI")
    async def test_compat_interface_with_project_id(
        self, mock_chat_openai, indexed_project: int
    ):
        """测试兼容接口（使用 project_id）"""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content="Test answer")
        )
        mock_chat_openai.return_value = mock_llm

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={
                    "project_id": indexed_project,
                    "message": "test question",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "answer" in data["data"]

    @patch("app.agents.qa_agent.ChatOpenAI")
    async def test_compat_interface_with_projectId_camelCase(
        self, mock_chat_openai, indexed_project: int
    ):
        """测试兼容接口（使用 projectId 驼峰命名）"""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content="Test answer")
        )
        mock_chat_openai.return_value = mock_llm

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={
                    "projectId": indexed_project,
                    "message": "test question",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    async def test_compat_interface_missing_project_id(self):
        """测试兼容接口缺少 project_id"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={
                    # 缺少 project_id
                    "message": "test",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1000  # PARAM_ERROR

    async def test_compat_interface_missing_message(self):
        """测试兼容接口缺少 message"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={
                    "project_id": 1,
                    # 缺少 message
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1000  # PARAM_ERROR

    async def test_compat_interface_invalid_types(self):
        """测试兼容接口参数类型错误"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={
                    "project_id": "not_int",  # 应该是整数
                    "message": 123,  # 应该是字符串
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 1000  # PARAM_ERROR


@pytest.mark.asyncio
class TestChatAPIEndToEnd:
    """端到端测试完整问答流程"""

    @patch("app.agents.qa_agent.ChatOpenAI")
    async def test_full_qa_workflow(
        self, mock_chat_openai, sample_repository_path: Path
    ):
        """测试完整的索引 + 问答工作流"""
        # Mock LLM
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(
                content="The User class is defined in src/main/java/com/example/User.java"
            )
        )
        mock_chat_openai.return_value = mock_llm

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

            # 步骤 2: 提问
            qa_response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": project_id,
                    "question": "Where is the User class defined?",
                },
            )

            assert qa_response.status_code == 200
            qa_data = qa_response.json()
            assert qa_data["code"] == 200
            assert "answer" in qa_data["data"]
            assert len(qa_data["data"]["sources"]) > 0

            # 验证 sources 结构
            for source in qa_data["data"]["sources"]:
                assert "file" in source
                assert "startLine" in source
                assert "endLine" in source

    @patch("app.agents.qa_agent.ChatOpenAI")
    async def test_multiple_questions_same_project(
        self, mock_chat_openai, indexed_project: int
    ):
        """测试对同一项目的多次提问"""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content="Answer")
        )
        mock_chat_openai.return_value = mock_llm

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 第一个问题
            response1 = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": indexed_project,
                    "question": "Question 1",
                },
            )

            # 第二个问题
            response2 = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": indexed_project,
                    "question": "Question 2",
                },
            )

            assert response1.status_code == 200
            assert response2.status_code == 200

            # 两次问答都应成功
            assert response1.json()["code"] == 200
            assert response2.json()["code"] == 200


@pytest.mark.asyncio
class TestChatAPIResponseFormat:
    """测试 API 响应格式规范"""

    @patch("app.agents.qa_agent.ChatOpenAI")
    async def test_response_has_standard_structure(
        self, mock_chat_openai, indexed_project: int
    ):
        """验证响应符合标准结构"""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content="Answer")
        )
        mock_chat_openai.return_value = mock_llm

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": indexed_project,
                    "question": "test",
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

        # 验证 data 内部结构
        assert "answer" in data["data"]
        assert "sources" in data["data"]
        assert isinstance(data["data"]["answer"], str)
        assert isinstance(data["data"]["sources"], list)

    async def test_error_response_has_standard_structure(self):
        """验证错误响应符合标准结构"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": 9999,  # 未索引
                    "question": "test",
                },
            )

        data = response.json()

        assert "code" in data
        assert "message" in data
        assert data["code"] == 2002  # INDEX_NOT_READY


@pytest.mark.asyncio
class TestChatAPISourcesMetadata:
    """测试答案来源（Sources）的元数据"""

    @patch("app.agents.qa_agent.ChatOpenAI")
    async def test_sources_contain_file_path(
        self, mock_chat_openai, indexed_project: int
    ):
        """验证 sources 包含文件路径"""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content="Answer")
        )
        mock_chat_openai.return_value = mock_llm

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat/ask",
                json={
                    "projectId": indexed_project,
                    "question": "test",
                },
            )

        data = response.json()
        sources = data["data"]["sources"]

        # 至少应有一个 source
        assert len(sources) > 0

        # 验证每个 source 的结构
        for source in sources:
            assert isinstance(source["file"], str)
            assert isinstance(source["startLine"], int)
            assert isinstance(source["endLine"], int)
            assert source["startLine"] > 0
            assert source["endLine"] >= source["startLine"]
