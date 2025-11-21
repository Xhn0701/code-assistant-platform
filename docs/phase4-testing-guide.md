# Phase 4 RAG Agent 测试与验证指南

## 📋 测试清单

### 1. 环境准备

**必需配置（.env）**：
```bash
# OpenAI 配置
OPENAI_API_KEY=sk-xxx...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MODEL=gpt-4o-mini

# Chroma 配置
CHROMA_PERSIST_DIRECTORY=./data/chroma

# 索引配置
INDEX_CHUNK_SIZE=1000
INDEX_CHUNK_OVERLAP=200
INDEX_MAX_FILE_SIZE=1048576

# Redis（可选，当前未使用）
REDIS_HOST=localhost
REDIS_PORT=6379
```

**检查依赖**：
```bash
cd agent-service
pip list | grep -E "(langchain|chromadb|openai|fastapi)"
```

---

### 2. 单元测试（推荐编写）

#### 测试文件结构
```
agent-service/tests/
├── __init__.py
├── conftest.py                    # pytest fixtures
├── unit/
│   ├── test_code_loader.py        # 代码加载器测试
│   ├── test_code_splitter.py      # 代码分块测试
│   ├── test_vectorstore.py        # 向量存储测试
│   └── test_embedding_service.py  # Embedding 服务测试
└── integration/
    ├── test_index_api.py          # 索引 API 集成测试
    └── test_chat_api.py           # 问答 API 集成测试
```

#### conftest.py（测试固件）
```python
import pytest
import tempfile
from pathlib import Path
from app.config import settings

@pytest.fixture(scope="function")
def temp_chroma_dir(tmp_path):
    """为每个测试提供独立的临时 Chroma 目录"""
    original_dir = settings.chroma_persist_directory
    test_dir = str(tmp_path / "chroma_test")
    settings.chroma_persist_directory = test_dir

    yield test_dir

    # 恢复原配置
    settings.chroma_persist_directory = original_dir

@pytest.fixture
def sample_code_file():
    """提供一个示例 Java 文件"""
    content = '''
public class UserController {
    @PostMapping("/login")
    public Result login(@RequestBody LoginRequest request) {
        // 验证用户名密码
        User user = userService.authenticate(request);
        if (user == null) {
            return Result.error("用户名或密码错误");
        }

        // 生成 JWT Token
        String token = jwtTokenProvider.generateToken(user);
        return Result.success(token);
    }
}
'''
    from app.models.code import CodeFile
    return CodeFile(
        project_id=1,
        path="UserController.java",
        language="java",
        content=content.strip(),
        size_bytes=len(content)
    )
```

#### test_code_splitter.py（示例）
```python
import pytest
from app.services.code_splitter import CodeSplitter

def test_split_code_file(sample_code_file):
    """测试代码分块功能"""
    splitter = CodeSplitter(chunk_size=200, chunk_overlap=50)
    chunks = splitter.split_code_file(sample_code_file)

    # 验证
    assert len(chunks) > 0, "应该生成至少一个代码块"
    assert all(chunk.project_id == 1 for chunk in chunks), "projectId 应一致"
    assert all(chunk.path == "UserController.java" for chunk in chunks), "路径应一致"
    assert all(chunk.start_line > 0 for chunk in chunks), "行号应从 1 开始"

    # 验证行号递增
    for i in range(len(chunks) - 1):
        assert chunks[i].end_line <= chunks[i+1].start_line, "行号应递增"

def test_approximate_line_numbers(sample_code_file):
    """测试近似行号计算"""
    splitter = CodeSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = splitter.split_code_file(sample_code_file)

    # 整个文件应该在一个 chunk 中
    assert len(chunks) == 1
    chunk = chunks[0]

    # 验证行号范围合理（允许 ±5 误差）
    actual_lines = sample_code_file.content.count("\n")
    assert abs(chunk.end_line - actual_lines) <= 5
```

#### test_index_api.py（集成测试示例）
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_index_local_repository(temp_chroma_dir):
    """测试索引本地仓库"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/index/repository",
            json={
                "projectId": 999,
                "repositoryUrl": "./tests/fixtures/sample_repo"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["status"] == "COMPLETED"
    assert data["data"]["totalFiles"] > 0

@pytest.mark.asyncio
async def test_index_status_not_found():
    """测试查询不存在的索引状态"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/index/status/9999")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 2002  # INDEX_NOT_READY
```

---

### 3. 手动验证流程

#### Step 1: 启动服务
```bash
cd agent-service

# 方式 1：直接运行
python main.py

# 方式 2：使用 uvicorn（开发模式）
uvicorn main:app --reload --port 8000

# 期望输出：
# ============================================================
# 🚀 Agent Service v0.1.0 启动中...
# 📝 调试模式: True
# 🔗 监听地址: http://0.0.0.0:8000
# 📚 API文档: http://0.0.0.0:8000/docs
# 🔍 健康检查: http://0.0.0.0:8000/health
# ============================================================
# INFO:     Application startup complete.
```

#### Step 2: 健康检查
```bash
# 基础健康检查
curl http://localhost:8000/api/v1/health

# 期望响应：
{
  "status": "healthy",
  "service": "Agent Service",
  "version": "0.1.0",
  "timestamp": "2025-11-20T12:00:00"
}
```

#### Step 3: 索引仓库
```bash
# 索引当前项目（修改路径为你的实际路径）
curl -X POST http://localhost:8000/api/v1/index/repository \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 1,
    "repositoryUrl": "E:/1study/AgentStudy/code-assistant-platform"
  }'

# 期望响应：
{
  "code": 0,
  "message": "索引成功",
  "data": {
    "projectId": 1,
    "status": "COMPLETED",
    "totalFiles": 156,
    "indexedFiles": 156,
    "errorMessage": null
  }
}

# 日志中应看到：
# [项目 1] 共加载 156 个文件
# [项目 1] 分块进度: 10% (15/156)
# [项目 1] 分块进度: 20% (31/156)
# ...
# [项目 1] 共生成 1523 个代码块
# [项目 1] 索引进度: 10%
# [项目 1] 索引进度: 20%
# ...
# [项目 1] 索引完成: 1523 文档
```

#### Step 4: 查询索引状态
```bash
curl http://localhost:8000/api/v1/index/status/1

# 期望响应：
{
  "code": 0,
  "data": {
    "projectId": 1,
    "status": "COMPLETED",
    "totalFiles": 156,
    "indexedFiles": 156,
    "errorMessage": null
  }
}
```

#### Step 5: RAG 问答测试
```bash
# 测试 1: 认证逻辑查询
curl -X POST http://localhost:8000/api/v1/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 1,
    "question": "这个项目的认证逻辑是如何实现的？"
  }'

# 期望响应：
{
  "code": 0,
  "message": "查询成功",
  "data": {
    "answer": "该项目使用 Spring Security + JWT 实现认证...",
    "sources": [
      {
        "file": "java-service/user-service/src/.../AuthController.java",
        "startLine": 45,
        "endLine": 80,
        "score": 0.89
      }
    ],
    "conversationId": null
  }
}

# 测试 2: 数据库相关查询
curl -X POST http://localhost:8000/api/v1/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 1,
    "question": "有哪些数据库表？"
  }'

# 测试 3: 前端相关查询
curl -X POST http://localhost:8000/api/v1/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 1,
    "question": "前端使用的是什么设计风格？"
  }'
```

#### Step 6: 错误场景测试
```bash
# 测试 1: 索引未完成时查询
curl -X POST http://localhost:8000/api/v1/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 9999,
    "question": "测试问题"
  }'

# 期望响应：
{
  "code": 2002,
  "message": "代码索引未完成，请先调用索引接口"
}

# 测试 2: 无效的仓库路径
curl -X POST http://localhost:8000/api/v1/index/repository \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 2,
    "repositoryUrl": "/invalid/path"
  }'

# 期望响应：
{
  "code": 2000,
  "message": "仓库路径无效或无权限访问",
  "data": {
    "path": "/invalid/path",
    "error": "目录不存在"
  }
}
```

---

### 4. 性能基线验证

#### 索引性能测试
```bash
# 记录索引时间
time curl -X POST http://localhost:8000/api/v1/index/repository \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 1,
    "repositoryUrl": "E:/1study/AgentStudy/code-assistant-platform"
  }'

# 性能目标：
# - 小型仓库（< 200 文件）：< 30s
# - 中型仓库（200-500 文件）：< 60s
# - 大型仓库（> 500 文件）：考虑异步任务
```

#### 问答性能测试
```bash
# 测试单次问答延迟
time curl -X POST http://localhost:8000/api/v1/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 1,
    "question": "认证逻辑如何实现？"
  }'

# 性能目标：
# - P50 延迟：< 3s
# - P95 延迟：< 5s
# - P99 延迟：< 10s
```

---

### 5. Swagger UI 测试

访问 http://localhost:8000/docs，测试以下场景：

1. **索引接口**：
   - 输入 projectId=1, repositoryUrl="本地路径"
   - 点击 Execute
   - 验证响应状态为 COMPLETED

2. **问答接口**：
   - 输入 projectId=1, question="测试问题"
   - 点击 Execute
   - 验证 sources 列表不为空

3. **状态查询**：
   - 输入 projectId=1
   - 验证返回 COMPLETED

---

### 6. 数据持久化验证

#### 检查 Chroma 持久化
```bash
# 查看 Chroma 数据目录
ls -lh ./data/chroma/

# 期望输出：
# chroma.sqlite3           # 元数据库
# <collection-uuid>/       # 集合数据

# 检查集合文件大小
du -sh ./data/chroma/

# 小型仓库（< 200 文件）预期：10-50MB
```

#### 服务重启测试
```bash
# 1. 停止服务（Ctrl+C）

# 2. 重新启动
python main.py

# 3. 查询索引状态（应该自动从 Chroma 推断）
curl http://localhost:8000/api/v1/index/status/1

# 期望：
# - status: COMPLETED
# - totalFiles/indexedFiles 为近似值（基于文档数）
```

---

### 7. 日志分析

#### 正常日志示例
```
2025-11-20 12:00:00 [INFO] main - 🚀 Agent Service v0.1.0 启动中...
2025-11-20 12:00:01 [INFO] vectorstore - ChromaDB 客户端已初始化: ./data/chroma
2025-11-20 12:01:15 [INFO] code_indexer - [项目 1] 共加载 156 个文件
2025-11-20 12:01:25 [INFO] code_indexer - [项目 1] 分块进度: 50% (78/156)
2025-11-20 12:01:30 [INFO] code_indexer - [项目 1] 共生成 1523 个代码块
2025-11-20 12:01:45 [INFO] code_indexer - [项目 1] 索引进度: 50%
2025-11-20 12:02:00 [INFO] code_indexer - [项目 1] 索引完成: 1523 文档
```

#### 异常日志排查
| 日志关键字 | 可能原因 | 解决方案 |
|-----------|---------|---------|
| `OPENAI_API_ERROR` | API Key 无效/限流 | 检查 .env 配置，确认账户额度 |
| `REPOSITORY_ERROR` | 路径无效 | 检查路径是否存在，权限是否正确 |
| `VECTOR_STORE_ERROR` | Chroma 操作失败 | 检查磁盘空间，删除损坏的集合 |
| `EMBEDDING_ERROR` | Embedding 生成失败 | 检查网络连接，API 配额 |

---

### 8. 常见问题排查

#### Q1: 索引时报错 "OPENAI_API_ERROR"
**原因**：API Key 无效或限流

**解决**：
```bash
# 1. 检查配置
echo $OPENAI_API_KEY

# 2. 测试 API 可用性
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 3. 检查账户额度
# https://platform.openai.com/usage
```

#### Q2: 问答结果不准确
**原因**：检索到的代码片段不相关

**调试**：
```python
# 临时修改 qa_agent.py，打印检索结果
docs = retriever.get_relevant_documents(question)
for i, doc in enumerate(docs):
    print(f"Doc {i}: {doc.metadata['path']}:{doc.metadata['start_line']}")
    print(f"Score: {doc.metadata.get('score', 'N/A')}")
    print(f"Content: {doc.page_content[:200]}...")
```

**优化方向**：
- 调整 `chunk_size`（当前 1000）
- 增加检索数量 `k`（当前 8）
- 优化 Prompt 模板

#### Q3: 服务重启后状态丢失
**正常现象**：当前使用内存存储，重启后状态推断逻辑会基于 Chroma 恢复

**验证**：
```bash
# 重启后查询
curl http://localhost:8000/api/v1/index/status/1

# 应该返回 COMPLETED（基于 Chroma 推断）
```

---

### 9. 测试覆盖率目标

**Phase 4 MVP 目标**：
- 单元测试覆盖率：≥ 70%
- 关键路径测试：100%（索引流程、问答流程）
- 集成测试：核心 API 全覆盖

**运行测试并生成报告**：
```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 运行测试
pytest tests/ -v --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

---

### 10. 验收清单

Phase 4 完成的标准：

- [ ] **核心功能**
  - [ ] 本地仓库索引成功
  - [ ] 问答返回合理答案
  - [ ] Sources 包含正确的文件路径和行号
  - [ ] 错误场景返回正确的错误码

- [ ] **性能指标**
  - [ ] 小型仓库索引 < 30s
  - [ ] 问答 P95 延迟 < 5s
  - [ ] 服务重启后状态自动恢复

- [ ] **文档完善**
  - [ ] PROJECTWIKI 更新 RAG 架构和 API 文档
  - [ ] CHANGELOG 记录详细变更
  - [ ] ADR 文档完成
  - [ ] 错误码说明完整

- [ ] **代码质量**
  - [ ] 单元测试覆盖率 ≥ 70%
  - [ ] 核心服务有完整的类型提示
  - [ ] 日志输出清晰（INFO/WARNING/ERROR）

---

**最后更新**: 2025-11-20
**维护者**: Phase 4 开发团队
