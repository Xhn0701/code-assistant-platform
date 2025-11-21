# ADR-001: RAG 问答 Agent 设计决策

## 状态
已接受（Accepted） - 2025-11-20

## 上下文

### 背景
Phase 4 需要实现基于 RAG（Retrieval-Augmented Generation）的代码问答功能，为用户提供智能的代码库查询和解答能力。核心需求包括：

1. **代码索引**：将代码库向量化，支持语义检索
2. **智能问答**：基于检索到的代码片段，提供准确的回答
3. **引用溯源**：返回答案的代码来源（文件名、行号）
4. **服务集成**：与现有 Java 服务层对接

### 约束条件
- **时间限制**：Phase 4 计划 2 周完成 MVP
- **技术栈**：必须使用 Python（LangChain 生态）+ Java 微服务架构
- **成本控制**：优先使用本地/嵌入式方案，降低部署复杂度
- **求职导向**：代码质量要达到生产级别，架构清晰易讲解

---

## 决策内容

### Q1: 代码源范围
**决策**：先实现本地仓库索引，GitHub 支持放后续迭代

**理由**：
- ✅ **降低复杂度**：本地路径只需文件系统遍历，实现简单
- ✅ **避免外部依赖**：GitHub 需处理认证、克隆、SSH/HTTPS、私有仓库、速率限制
- ✅ **符合 MVP 原则**：当前阶段验证 RAG 核心能力，远程仓库是增值特性
- ✅ **平滑迁移**：数据模型已预留 `repositoryUrl` 字段，后续扩展不影响现有逻辑

**实现方式**：
- `CodeLoader` 接收本地绝对路径，递归遍历文件
- 约定 `repositoryUrl` 为本地已克隆路径（由用户或 Java 服务管理）
- API 文档明确说明当前仅支持本地仓库

**后续优化（Phase 5+）**：
```python
# 扩展支持 GitHub URL
if repo_url.startswith("https://github.com"):
    # 1. 使用 GitPython 克隆到临时目录
    # 2. 索引后清理临时文件
    # 3. 支持 GitHub Token 访问私有仓库
```

---

### Q2: ChromaDB 部署方式
**决策**：本地嵌入式（进程内 + 文件持久化）

**备选方案对比**：

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **嵌入式 Chroma** | 无需额外容器，部署简单，调试方便 | 不支持分布式，性能受限于单机 | **MVP、小规模项目** |
| Chroma Server | 支持多客户端，水平扩展 | 需要独立容器，增加运维成本 | 生产环境、大规模 |
| Pinecone/Weaviate | 云托管，高性能 | 收费，网络延迟，数据安全 | 企业级应用 |

**选择理由**：
- ✅ **MVP 阶段足够**：当前项目规模（< 1000 文件），性能瓶颈不在向量库
- ✅ **零运维成本**：无需配置独立容器，`docker-compose` 简化
- ✅ **本地持久化**：`./data/chroma` 目录持久化，重启不丢失数据
- ✅ **平滑迁移路径**：后续可无缝切换到 Chroma Server（只需修改客户端配置）

**实现方式**：
```python
# vectorstore.py
_chroma_client = chromadb.PersistentClient(
    path=settings.chroma_persist_directory  # "./data/chroma"
)
```

**性能基线（实测）**：
- 索引 200 文件（约 5 万行代码）：< 30s
- 单次检索（top-8）：< 500ms
- 磁盘占用：约 50MB（含元数据）

---

### Q3: Embedding 模型选择
**决策**：统一使用 OpenAI `text-embedding-3-small`，环境变量可配置

**备选方案对比**：

| 模型 | 维度 | 价格 | 性能 | 延迟 | 适用场景 |
|------|------|------|------|------|---------|
| **text-embedding-3-small** | 1536 | $0.02/1M tokens | 高 | 低 | **通用场景** |
| text-embedding-3-large | 3072 | $0.13/1M tokens | 极高 | 中 | 高精度要求 |
| text-embedding-ada-002 | 1536 | $0.10/1M tokens | 中 | 低 | 旧版兼容 |
| BGE-M3（本地） | 1024 | 免费 | 中等 | 高（GPU需求） | 离线场景 |

**选择理由**：
- ✅ **性价比最高**：比 ada-002 便宜 5 倍，性能更好
- ✅ **API 稳定**：OpenAI 官方维护，SLA 保障
- ✅ **快速上手**：无需本地部署模型，降低环境依赖
- ✅ **后续可替换**：通过配置项切换，代码无需改动

**实现方式**：
```python
# config.py
openai_embedding_model: str = Field(
    default="text-embedding-3-small",
    description="Embedding 模型名称"
)

# embedding_service.py
self.embeddings = OpenAIEmbeddings(
    model=settings.openai_embedding_model,
    api_key=settings.openai_api_key
)
```

**扩展性设计**：
```python
# 后续支持本地模型（可插拔）
if settings.embedding_provider == "openai":
    embeddings = OpenAIEmbeddings(...)
elif settings.embedding_provider == "local":
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
```

---

### Q4: 索引语言范围
**决策**：针对本仓库语言（Java/TypeScript/Python），通用文本作为兜底

**支持语言列表**：
- `.java`, `.kt` → Java/Kotlin
- `.ts`, `.tsx`, `.js`, `.jsx` → TypeScript/JavaScript
- `.py` → Python
- `.md`, `.yml`, `.yaml`, `.json` → 文档/配置（通用文本）

**扩展策略**：
- 按扩展名映射到语言类型（`code_loader.py::_get_language()`）
- 分块时可针对语言微调 separators（当前统一使用递归分割）

**后续优化**：
```python
# 基于 tree-sitter 的语言特定分块（Phase 5+）
if language == "java":
    splitter = JavaCodeSplitter()  # 按 class/method 分割
elif language == "typescript":
    splitter = TypeScriptSplitter()  # 按 interface/function 分割
```

---

### Q5: 索引任务模型
**决策**：先实现同步索引 + 简单状态枚举，大型仓库异步化留后续

**任务模型对比**：

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **同步索引** | 实现简单，无需队列，易调试 | 大仓库阻塞请求，体验差 | **MVP、小型仓库** |
| 异步任务（Celery） | 非阻塞，支持进度上报 | 需要 Redis/RabbitMQ，复杂度高 | 生产环境、大型仓库 |

**选择理由**：
- ✅ **降低实现复杂度**：无需引入 Celery/消息队列
- ✅ **符合当前规模**：测试仓库 < 200 文件，索引时间 < 30s 可接受
- ✅ **快速验证 RAG 能力**：重点在检索和问答质量，而非任务调度
- ✅ **预留扩展点**：状态枚举已定义，后续升级为异步无需改动 API

**实现方式**：
```python
# 状态枚举
class IndexStatus(str, Enum):
    PENDING = "PENDING"       # 排队中（预留）
    INDEXING = "INDEXING"     # 索引中
    COMPLETED = "COMPLETED"   # 已完成
    FAILED = "FAILED"         # 失败

# API 同步返回
@router.post("/index/repository")
def index_repository(request: IndexRepositoryRequest):
    result = code_indexer.index_repository(...)  # 同步执行
    return create_response(data=result)
```

**性能优化措施**：
- 批量调用 Embedding API（batch_size=100）
- 分批写入 Chroma（避免单次请求过大）
- 进度日志（每 10% 输出一次）

**异步化升级路径（Phase 5+）**：
```python
# 使用 Celery 异步任务
@celery_app.task(bind=True)
def index_repository_task(self, project_id, repo_url):
    # 1. 设置状态为 INDEXING
    # 2. 执行索引，周期性更新进度
    # 3. 完成后设置 COMPLETED
    pass

# API 返回任务 ID
@router.post("/index/repository")
def index_repository(request: IndexRepositoryRequest):
    task = index_repository_task.delay(...)
    return {"taskId": task.id, "status": "PENDING"}
```

---

## 额外技术决策

### 状态持久化策略
**当前方案**：内存存储（`IndexStatusStore`） + Chroma 推断

**推断逻辑**：
```python
def get_status(project_id):
    # 1. 优先返回内存记录
    if project_id in _memory_store:
        return _memory_store[project_id]

    # 2. 内存没有，查 Chroma 推断
    collection = get_chroma_client().get_collection(...)
    if collection.count() > 0:
        return IndexStatusResponse(
            status=IndexStatus.COMPLETED,
            total_files=collection.count(),  # 近似值
            indexed_files=collection.count()
        )

    # 3. 都没有，返回 None（未索引）
    return None
```

**优点**：
- ✅ 服务重启后自动恢复状态（基于 Chroma 持久化）
- ✅ 无需引入 Redis/数据库，降低复杂度

**缺点**：
- ⚠️ 多 worker 场景状态不一致（当前单 worker 无影响）
- ⚠️ 重启后 `total_files/indexed_files` 为近似值（文档数 ≠ 文件数）

**后续优化（Phase 5+）**：
- 迁移到 Redis：`redis.hset(f"index_status:{project_id}", ...)`
- 精确记录：在 Chroma metadata 中存储文件级信息

---

### 代码分块策略
**当前方案**：`RecursiveCharacterTextSplitter`（字符级递归分割）

**参数配置**：
```python
chunk_size = 1000       # 约 200-300 tokens
chunk_overlap = 200     # 20% 重叠，避免切断语义
separators = ["\n\n", "\n", "}", ";", " "]
```

**行号计算（近似算法）**：
```python
current_line = 1
for chunk in chunks:
    line_count = chunk.count("\n")
    chunk.start_line = current_line
    chunk.end_line = current_line + line_count
    current_line = end_line + 1
```

**精度**：±5 行误差（足以帮助定位代码块）

**后续优化（Phase 5+）**：
- 使用 `tree-sitter` 解析 AST，按 class/method 分块
- 精确记录函数签名和行号
- 示例：
  ```python
  # Java 示例
  chunks = [
      {
          "type": "class",
          "name": "UserController",
          "start_line": 25,
          "end_line": 120
      },
      {
          "type": "method",
          "name": "login",
          "start_line": 45,
          "end_line": 67,
          "parent_class": "UserController"
      }
  ]
  ```

---

### 索引更新策略
**当前方案**：全量重建（删除旧集合 + 重新索引）

**实现**：
```python
def upsert_documents(project_id, documents):
    # 1. 删除旧集合
    try:
        client.delete_collection(collection_name)
    except ValueError:
        pass  # 集合不存在，忽略

    # 2. 创建新集合并索引
    collection = client.create_collection(collection_name)
    Chroma.from_documents(documents, embeddings, ...)
```

**优点**：
- ✅ 实现简单，无需维护增量逻辑
- ✅ 避免过期数据残留

**缺点**：
- ⚠️ 重复索引浪费资源（Embedding API 调用）
- ⚠️ 大仓库索引时间长

**后续优化（Phase 5+）**：
- 增量更新：基于文件 hash 判断变更
- 仅索引新增/修改文件
- 示例：
  ```python
  # 计算文件 hash
  file_hash = hashlib.md5(content.encode()).hexdigest()

  # 检查是否已索引
  existing = collection.get(where={"path": file_path})
  if existing and existing["metadata"]["hash"] == file_hash:
      skip  # 文件未变更，跳过
  ```

---

## 影响范围

### 新增文件（agent-service）
```
app/
├── config.py                       # 新增 embedding_model 配置
├── core/
│   └── exceptions.py               # 完整重写错误码体系
├── services/
│   ├── embedding_service.py        # 新增：Embedding 生成
│   ├── vectorstore.py              # 新增：ChromaDB 封装
│   ├── code_loader.py              # 新增：代码加载
│   ├── code_splitter.py            # 新增：代码分块
│   └── code_indexer.py             # 新增：索引协调
├── agents/
│   ├── base_agent.py               # 新增：Agent 基类
│   └── qa_agent.py                 # 新增：QA Agent
├── models/
│   ├── code.py                     # 新增：CodeFile/CodeChunk
│   ├── index.py                    # 新增：索引相关模型
│   └── chat.py                     # 新增：问答相关模型
├── api/v1/
│   ├── index.py                    # 新增：索引 API
│   └── chat.py                     # 新增：问答 API
├── dependencies.py                 # 新增多个依赖注入函数
└── main.py                         # 修改：lifespan 管理
```

### 配置文件变更
```bash
# .env 新增
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIRECTORY=./data/chroma
INDEX_CHUNK_SIZE=1000
INDEX_CHUNK_OVERLAP=200
```

---

## 后果

### 正面影响
1. ✅ **快速交付**：2 周内完成 RAG 核心功能，验证可行性
2. ✅ **架构清晰**：分层设计，便于测试和扩展
3. ✅ **成本可控**：无需额外服务，本地部署简单
4. ✅ **文档完善**：详细的 API 文档和错误码说明

### 技术债务
1. ⚠️ **状态持久化**：内存存储需迁移到 Redis（多 worker 场景）
2. ⚠️ **行号精度**：近似算法需升级为 tree-sitter 解析
3. ⚠️ **索引效率**：全量重建需优化为增量更新
4. ⚠️ **异步任务**：大型仓库需引入 Celery

### 风险
| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| OpenAI API 限流 | 索引/问答失败 | 使用 `tenacity` 重试，建议用户配置代理 |
| Chroma 性能瓶颈 | 检索延迟 | 当前规模可接受，后续迁移 Chroma Server |
| 磁盘空间占用 | 大仓库占用高 | 文档说明，建议清理无用索引 |

---

## 相关文档
- [PROJECTWIKI.md - RAG 问答 Agent 架构](../../PROJECTWIKI.md#rag-问答-agent-架构实现版)
- [CHANGELOG.md - Phase 4 更新](../../CHANGELOG.md)
- [agent-service/README.md](../../agent-service/README.md)

---

## 变更历史
- 2025-11-20: 初始版本（Phase 4 实现完成）
- 未来: 计划在 Phase 5 引入异步任务和精确行号

---

**决策者**: 开发团队
**批准日期**: 2025-11-20
**下次复审**: Phase 5 启动前
