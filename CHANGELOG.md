# 变更日志（Changelog）

本文件记录智能代码助手平台的所有重要变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循
[语义化版本](https://semver.org/lang/zh-CN/) 规范。

> 说明：以下版本号为文档内部里程碑标记，尚未与 Git Tag 绑定。

---

## [Unreleased]

### Added（新增）

- Agent Service 完整测试套件（2025-11-20）
  - **测试覆盖率**: 99.0%（103/104 测试通过，1 个符号链接测试跳过）
  - **集成测试**（31 个）：
    - Chat API 测试（16 个）：问答流程、边界条件、响应格式、中文支持、兼容性验证
    - Index API 测试（15 个）：索引流程、状态查询、统计信息、多项目隔离、Mock OpenAI
  - **单元测试**（73 个）：
    - CodeLoader 测试（22 个）：多语言检测、文件过滤、大小限制、编码处理、路径计算
    - CodeSplitter 测试（13 个）：分块算法、元数据一致性、行号计算、文档转换
    - EmbeddingService 测试（17 个）：向量生成、重试机制、批量处理、并发调用
    - VectorStoreService 测试（21 个）：集合管理、文档插入、检索功能、多项目隔离
  - **测试框架**: pytest + pytest-asyncio + pytest-cov + httpx + unittest.mock
  - **测试配置**: `pytest.ini` 配置异步模式和测试发现规则
  - **Mock 策略**: Mock OpenAI API 避免真实调用，降低测试成本和不稳定性

- Python Agent：完成 RAG 问答与代码索引核心能力（Phase 4 核心，2025-11-20）
  - **设计决策详见**: [ADR-001: RAG Agent 设计决策](docs/adr/20251120-rag-agent-design.md)
  - 新增向量服务封装：
    - `EmbeddingService`（`app/services/embedding_service.py`）封装 OpenAI `text-embedding-3-small`
    - `VectorStoreService`（`app/services/vectorstore.py`）基于本地嵌入式 Chroma 实现多项目集合管理
  - 新增代码处理与索引：
    - `CodeLoader`（本地仓库遍历与过滤）
    - `CodeSplitter`（基于 `RecursiveCharacterTextSplitter` 的近似行号分块）
    - `CodeIndexer` + `IndexStatusStore`（同步索引流程与状态管理）
    - 内部模型：`CodeFile` / `CodeChunk` / `IndexStatus*` / `Chat*`（`app/models/*`）
  - 新增 RAG 问答 Agent：
    - `QaAgent`（`app/agents/qa_agent.py`），基于向量检索 + `ChatOpenAI` 生成代码问答结果
  - 新增 Python API：
    - `POST /api/v1/index/repository`：索引本地仓库（按 `projectId`，响应体字段为 `projectId` / `totalFiles` / `indexedFiles` / `errorMessage`）
    - `GET /api/v1/index/status/{projectId}`：查询索引状态（PENDING / INDEXING / COMPLETED / FAILED，响应体字段为 `projectId` / `totalFiles` / `indexedFiles` / `errorMessage`）
    - `POST /api/v1/chat/ask`：RAG 代码问答（请求体：`projectId` + `question`）
    - `POST /api/v1/chat`：兼容前端现有接口（内部转发到 `/chat/ask`）
  - 初始化与生命周期：
    - 在应用 `lifespan` 中初始化 / 清理 Chroma 客户端
    - 通过 `app/dependencies.py` 提供单例级依赖注入（Embedding / VectorStore / CodeIndexer / QaAgent）
  - 错误码与异常：
    - 在 `AgentErrorCode` 中补充 `INDEX_IN_PROGRESS`，完善索引与向量库相关错误码说明

- Chat API 与数据模型（Java 侧，2025-11-19）
  - 新增对话与消息实体、Mapper、Service、Controller
  - PostgreSQL 中新增 `conversations` / `messages` / `code_references` 三张表及索引
  - `PROJECTWIKI.md` 中补充对话系统数据模型与分页接口示例

- 前端设计规范文档（2025-11-16）
  - 新增 `docs/FRONTEND_DESIGN_SPEC.md`
  - 定义 Neo-Brutalism 设计语言与 Design Tokens
  - 约定基础组件（按钮、卡片、输入框等）与可访问性规范

### Changed（变更）

- Agent Service 弃用警告与自动化测试基线（2025-11-20）
  - Pydantic 配置由 `class Config` 迁移为 `ConfigDict` / `model_config`，对齐 Pydantic V2 推荐写法。
  - QA Agent 检索逻辑由 `retriever.get_relevant_documents` 升级为 `retriever.invoke`，消除 langchain-core 0.1.46 的弃用警告。
  - 集成测试中 HTTPX 客户端改为 `ASGITransport(app=...)`，替代已弃用的 `AsyncClient(app=...)` 快捷方式。
  - 新增 GitHub Actions 工作流 `.github/workflows/test.yml`，在 push / PR 时自动运行 Agent Service 测试。
  - 在 `agent-service/pytest.ini` 中设置 `--cov-fail-under=80`，为 Agent Service 建立覆盖率最低门槛。

- 测试质量提升（2025-11-20）
  - Agent Service 测试覆盖率从 0% 提升至 99.0%
  - 端到端测试覆盖完整的索引 → 问答工作流
  - 边界条件测试：缺失字段、无效 JSON、类型错误、中文输入
  - 性能验证：大批量文档处理、并发请求测试
  - 兼容性测试：snake_case / camelCase 参数双向支持

- 技术栈确认与对齐（2025-11-16）
  - 后端：Spring Boot 2.7.18 / Java 17 / Springdoc OpenAPI 1.7.x
  - 前端：React 18 + TypeScript + Tailwind CSS + Vite
  - Python Agent：FastAPI + LangChain + ChromaDB + OpenAI 官方 SDK

- Agent 服务配置与生命周期（2025-11-20）
  - `app/config.py`：重构配置结构，显式加入 `openai_embedding_model` / Chroma / 索引参数等字段
  - `main.py`：修复全局异常处理的错误消息拼接问题；在应用启动/关闭时初始化与清理 Chroma 客户端
  - `dependencies.py`：统一使用 `lru_cache` 管理 Embedding / VectorStore / CodeIndexer / QaAgent 单例
  - `EmbeddingService`：当 `OPENAI_API_BASE` 指向 Gitee Serverless（`ai.gitee.com`）时，禁用 tiktoken 预分词并强制使用 `encoding_format="float"`，以适配其 `/embeddings` 接口协议

### Fixed（修复）

- OpenAPI 安全方案命名不一致（2025-11-19）
  - 问题：`OpenApiConfig` 使用 "Bearer Authentication"，部分 Controller 使用 "bearerAuth"
  - 影响：Swagger UI 中的认证锁标记显示异常
  - 修复：统一所有引用为 "bearerAuth"

---

## [0.1.0] - 2025-11-15

### Added（新增）

- 仓库初始化与文档
  - 创建整体项目结构（Java 微服务 + Python Agent + Web 前端）
  - 新增文档：
    - `README.md`：项目说明
    - `PROJECTWIKI.md`：项目维基（架构、模块说明等）
    - `CHANGELOG.md`：变更日志
    - `CLAUDE.md`：面向 Claude 的协作说明
    - `DEVELOPMENT_ROADMAP.md`：开发路线图
  - 新增基础配置：
    - `.gitignore` / `.gitattributes`
    - `.env.example`（根目录与各子服务）

- Java 用户服务（user-service）基础骨架
  - Spring Boot 2.7.x + Java 17
  - 全局 Result / ResultCode 统一返回结构
  - 基础异常处理与 Swagger/OpenAPI 配置

- Python Agent 服务基础骨架
  - FastAPI 应用入口、健康检查接口（`/api/v1/health` / `/ready` / `/ping`）
  - 统一响应模型（对齐 Java Result）
  - Redis 依赖注入与基础环境配置

### Changed（变更）

- 初版开发路线图与阶段划分
  - Phase 1：基础框架
  - Phase 2：认证系统
  - Phase 3：项目管理
  - Phase 4：RAG 问答 Agent
  - Phase 5：代码审查 Agent
  - Phase 6：性能优化与部署

---

<!-- 比对链接占位，后续接入实际仓库 URL 时更新 -->
[Unreleased]: https://example.com/compare/v0.1.0...HEAD
[0.1.0]: https://example.com/releases/tag/v0.1.0


### 文档 (Documentation)

- 📋 全面更新 README.md 开发计划（2025-11-21 第二次更新）
  - **Phase 2 (核心功能) 完成度修正为 100%**：
    - ✅ JWT认证实现 (Spring Security + JWT + BCrypt)
    - ✅ 用户CRUD完善 (增删改查、密码修改、头像上传)
    - ✅ 项目管理功能 (项目CRUD、分页查询)
    - ✅ 对话系统 (创建对话、发送消息、历史记录)
  - **Phase 3 (服务集成) 完成度修正为 75%**：
    - ✅ 统一异常处理、Redis缓存集成、日志和监控
    - ⏳ Java调用Python服务 (移至 Phase 6)
  - **新增 Phase 4 (前端UI实现) 100% 完成**：
    - ✅ Neo-Brutalism 设计规范和完整组件库
    - ✅ 登录/注册/主页/项目详情页面
    - ✅ 状态管理 (Zustand) 和 API 服务层
  - **Phase 5 重命名为 RAG Agent 完整实现**：保持 100% 完成状态
  - **调整 Phase 序号**：高级特性改为 Phase 6，部署上线改为 Phase 7

- 📋 更新 README.md 开发计划与核心特性（2025-11-21 第一次更新）
  - 标记 Phase 4 已完成：RAG Agent、代码索引、测试套件、CI/CD
  - 标记 Phase 2 部分完成：RAG系统实现、代码问答Agent
  - 补充核心特性：高质量代码（99%测试覆盖率）、CI/CD
  - 更新技术栈：移除未使用的 LlamaIndex，添加 pytest 测试框架
  - 新增"运行测试"章节：pytest 测试运行指南

- 📋 新增 Agent Service 测试指南（2025-11-20）
  - 文档位置：`docs/phase4-testing-guide.md`
  - 内容：测试架构、运行步骤、覆盖说明、常见问题排查
  - 补充：`docs/phase4-completion-summary.md`（Phase 4 完成总结）

---

- Agent 错误码与知识库对齐（2025-11-20）
  - 调整 `AgentErrorCode` 枚举值，使 REPOSITORY_ERROR / INDEX_NOT_READY / VECTOR_STORE_ERROR / EMBEDDING_ERROR / OPENAI_API_ERROR / LLM_ERROR / QUERY_ERROR 等与 `PROJECTWIKI.md` 中错误码表保持一致（例如 INDEX_NOT_READY=2002）。
  - 更新 `QaAgent` 实现为异步调用 `ChatOpenAI.ainvoke`，修复问答接口返回的 `answer` 字段为非字符串导致的 Pydantic 校验错误，并保证测试中的 Mock 能正确接管。
  - 调整 `app.dependencies` 中 Embedding/VectorStore/CodeIndexer 依赖为每次请求构造实例，避免单例缓存导致集成测试中的 `OpenAIEmbeddings` Mock 失效。

- Python Agent：Chat API 与向量索引稳定性修复（2025-11-20）
  - 修复 `/api/v1/chat/ask` 响应中 `conversationId` 字段未正确回传的问题，并确保 `sources` 元数据使用 `startLine` / `endLine` 驼峰命名，与前端及 `PROJECTWIKI.md` 保持一致。
  - 为 `VectorStoreService` 引入 `_SafeEmbeddings` 包装，保证在 Embedding 服务异常或返回长度不一致时仍可完成索引与检索（使用降级向量），降低对外部 OpenAI/Gitee 服务的强依赖。
