# 更新日志 (Changelog)

本文档记录项目的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [未发布] - 开发中

### 新增 (Added)
- ✅ **Chat API（对话与消息）实现** (2025-11-19)
  - Java：新增 ChatController/Service/DTO/实体/Mapper；实现对话创建、列表、消息发送、历史查询与分页
  - DB：新增 V3 迁移脚本，创建 `conversations`、`messages`、`code_references` 表与必要索引/触发器
  - 文档：`PROJECTWIKI.md` 补充“Chat API 分页接口”示例（见“附录：Chat API 补充”）
  - 参考：Java API 文档“对话与消息接口（Chat API）”小节
- ✅ **前端设计规范文档** (2025-11-16)
  - 创建 `docs/FRONTEND_DESIGN_SPEC.md`
  - 定义 Neo-Brutalism 设计系统
  - 包含完整的 Design Tokens
  - 提供基础组件规范（BrutButton, BrutCard, BrutInput等）
  - 添加可访问性要求和 Do/Don't 清单

- ✅ **对话系统数据模型（会话 / 消息 / 代码引用）** (2025-11-16)
  - 在 PostgreSQL 中新增 `conversations`、`messages`、`code_references` 三张表及核心索引
  - 在 `java-service/user-service` 中新增对应实体和 Mapper（Conversation / Message / CodeReference）
  - 在 `PROJECTWIKI.md` 中补充“对话系统数据模型（实现版）”小节及 Mermaid 图，作为最新实现的权威描述

### 变更 (Changed)
- ✅ **技术栈版本确认** (2025-11-16)
  - Spring Boot: 2.7.18
  - Java版本: 17
  - OpenAPI 文档: Springdoc OpenAPI UI 1.7.0
  - 理由: 兼顾稳定性与现代特性，生态成熟
- ✅ **调整JWT版本** (2025-11-16)
  - JJWT: 0.12.3 → 0.11.5（与 Boot 2.7 组合稳定）

### 技术决策
#### 版本与框架选择
1. **稳定优先**: Spring Boot 2.7.x 生态成熟、资料丰富
2. **现代语言特性**: Java 17 LTS，长期支持
3. **文档与兼容**: Springdoc OpenAPI 1.7.x 与 Boot 2.7 组合稳定
4. **迁移路径**: 后续可平滑升级至 Boot 3.x + 新 Security DSL

#### 前端技术选型 (2025-11-16)
**技术栈**: React 18 + TypeScript + Tailwind CSS + Vite

**设计风格**: Neo-Brutalism（新粗野主义）+ 硬阴影贴纸感

**选型理由**:
1. **React**: 求职市场需求最大，生态最成熟
2. **TypeScript**: 类型安全，减少运行时错误
3. **Tailwind CSS**: 原子化样式，快速实现设计风格
4. **Vite**: 开发体验极佳，热更新迅速
5. **Neo-Brutalism风格**:
   - 高对比度，可访问性好
   - 实现简单，不需要复杂的动画
   - 视觉独特，面试展示有辨识度
   - 拒绝模糊阴影/渐变/玻璃拟态

**详细规范**: `docs/FRONTEND_DESIGN_SPEC.md`

### 计划添加
- [ ] 用户认证系统完整实现
- [ ] 项目管理CRUD接口
- [ ] RAG问答Agent核心功能
- [ ] 代码索引服务
- [ ] 代码审查Agent基础版
- [ ] Docker-compose完整配置
- [ ] API接口文档完善
- [ ] 单元测试框架搭建

---

### 备注（对话 API）
- Java 对话 API（ChatController + ChatService 初版）已实现，详见 PROJECTWIKI.md 中的 Chat API 小节。

## [0.1.0] - 2025-11-15

### 新增 (Added)

#### 项目初始化
- ✅ 创建项目整体目录结构（微服务架构）
- ✅ 创建README.md项目说明文档
- ✅ 创建PROJECTWIKI.md项目维基文档
- ✅ 创建CHANGELOG.md变更日志文档
- ✅ 创建.gitignore配置文件
- ✅ 创建.env.example环境变量模板

#### Java服务基础框架
- ✅ user-service目录结构创建
  - controller/ - API控制器层
  - service/ - 业务逻辑层
  - mapper/ - 数据访问层
  - entity/ - 实体类
  - dto/ - 数据传输对象
  - security/ - 安全认证
  - config/ - 配置类
- ✅ project-service目录结构创建
- ✅ Maven pom.xml配置文件
  - Spring Boot 3.2.0
  - Spring Security
  - MyBatis-Plus 3.5.5
  - JWT 0.12.3
  - PostgreSQL Driver
  - Redis
  - Springdoc OpenAPI
- ✅ application.yml配置文件
  - 数据库连接配置
  - Redis连接配置
  - MyBatis-Plus配置
  - JWT配置
  - 日志配置
  - Swagger配置

#### Python Agent服务框架
- ✅ agent-service目录结构创建
  - app/api/v1/ - API路由
  - app/agents/ - Agent实现
  - app/services/ - 业务服务
  - app/models/ - 数据模型
  - app/core/ - 核心配置
  - tests/ - 测试

#### 文档
- ✅ 完整的项目架构文档（PROJECTWIKI.md）
  - 整体架构设计图
  - 服务职责划分
  - 技术栈详解
  - 模块说明
  - API接口文档模板
  - 数据库设计
  - 开发指南
  - 部署指南
  - 常见问题FAQ
- ✅ AI助手维护指南（CLAUDE.md）
  - 文档更新规则和时机
  - PROJECTWIKI.md维护规范
  - CHANGELOG.md维护规范
  - 格式规范和图标使用
  - 实际操作示例
  - 文档质量检查清单
- ✅ 详细开发路线图（DEVELOPMENT_ROADMAP.md）
  - 6个开发阶段完整规划
  - 每个Task的前置条件
  - 详细的开发步骤和代码要求
  - 明确的完成标准和验收测试
  - 文档更新要求
  - 预估时间和进度追踪

### 技术决策

#### 为什么选择微服务架构？
1. **技术展示需求**: 需要同时展示Java和Python能力
2. **职责分离**: 业务逻辑(Java)与AI推理(Python)分离，符合单一职责原则
3. **技术栈优势**: Java擅长事务处理，Python适合AI/ML任务
4. **求职导向**: 微服务经验在招聘中是加分项
5. **可扩展性**: 未来可以独立扩展各个服务

#### 为什么选择这些技术栈？

**Java侧:**
- **Spring Boot 3.2**: 最新稳定版，社区活跃，文档完善
- **MyBatis-Plus**: 比JPA灵活，比MyBatis简洁，适合快速开发
- **JWT**: 无状态认证，适合微服务架构
- **Redis**: 高性能缓存，降低数据库压力

**Python侧:**
- **FastAPI**: 性能高，文档自动生成，异步支持好
- **LangChain**: Agent开发标准框架，生态完善
- **ChromaDB**: 轻量级向量库，易于部署和调试

#### 为什么不用Spring Cloud全家桶？
1. **复杂度控制**: Eureka、Config Server等增加学习成本
2. **时间限制**: 3-4个月需要快速产出MVP
3. **过度设计**: 2-3个服务不需要完整的微服务治理
4. **求职定位**: Agent开发岗更看重AI能力而非微服务治理

### 架构特点

#### 优点
- ✅ **职责清晰**: Java处理业务，Python处理AI
- ✅ **技术全面**: 展示全栈能力
- ✅ **易于理解**: 架构简单，面试容易讲清楚
- ✅ **可扩展**: 后续可以添加更多Agent

#### 权衡
- ⚠️ **复杂度适中**: 比单体复杂，但不过度设计
- ⚠️ **服务通信**: HTTP REST，性能够用但非最优
- ⚠️ **事务处理**: 分布式事务暂时不考虑，采用补偿机制

---

## 开发计划

### Phase 1: 基础框架搭建 (Week 1-2) - 进行中

**目标**: 完成项目框架，服务可以启动

#### Java服务
- [x] 项目结构创建
- [x] Maven配置
- [x] application.yml配置
- [ ] UserServiceApplication.java启动类
- [ ] 基础配置类(RedisConfig, SwaggerConfig)
- [ ] 统一返回格式(Result类)
- [ ] 全局异常处理

#### Python服务
- [ ] requirements.txt依赖配置
- [ ] main.py FastAPI启动类
- [ ] config.py配置管理
- [ ] 统一响应格式
- [ ] 异常处理中间件

#### 基础设施
- [ ] docker-compose.yml编排配置
- [ ] PostgreSQL初始化脚本
- [ ] Redis配置
- [ ] Nginx配置

**交付物**:
- 所有服务可以启动
- Swagger文档可以访问
- 数据库连接成功

---

### Phase 2: 用户认证实现 (Week 3-4)

**目标**: 完整的用户注册、登录、JWT认证

#### 功能清单
- [ ] User实体类和数据库表
- [ ] UserMapper数据访问层
- [ ] 用户注册接口（密码BCrypt加密）
- [ ] 用户登录接口（JWT生成）
- [ ] JwtTokenProvider工具类
- [ ] JwtAuthenticationFilter过滤器
- [ ] SecurityConfig安全配置
- [ ] Token刷新接口
- [ ] 用户信息查询接口
- [ ] Redis缓存用户信息

#### 测试要求
- [ ] 注册接口单元测试
- [ ] 登录接口集成测试
- [ ] JWT验证测试
- [ ] Postman接口测试集合

**交付物**:
- 完整的认证流程
- API测试通过
- 代码覆盖率>70%

---

### Phase 3: 项目管理实现 (Week 5-6)

**目标**: 项目CRUD、GitHub仓库接入

#### 功能清单
- [ ] Project实体类和数据库表
- [ ] 项目创建接口
- [ ] 项目列表查询（分页）
- [ ] 项目详情查询
- [ ] 项目更新接口
- [ ] 项目删除（逻辑删除）
- [ ] GitHub仓库URL验证
- [ ] 调用Python服务索引代码

#### Java → Python调用
- [ ] RestTemplate/OpenFeign配置
- [ ] AgentClientService服务类
- [ ] 异步调用和回调

**交付物**:
- 项目管理功能完整
- 服务间调用成功

---

### Phase 4: RAG问答Agent (Week 7-8)

**目标**: 基于RAG的代码问答

#### Python Agent开发
- [ ] ChromaDB集成
- [ ] 代码文件加载器
- [ ] 代码分块策略（RecursiveTextSplitter）
- [ ] Embedding生成（OpenAI/本地）
- [ ] 向量存储和检索
- [ ] LangChain QA Chain
- [ ] 对话历史管理
- [ ] 引用来源返回

#### API接口
- [ ] POST /api/v1/index/repository - 索引仓库
- [ ] POST /api/v1/chat/ask - 代码问答
- [ ] GET /api/v1/chat/history - 对话历史

#### 优化
- [ ] 混合检索策略（Dense + Sparse）
- [ ] 检索结果重排序
- [ ] 缓存热门问题

**交付物**:
- 问答功能可用
- 检索准确率测试

---

### Phase 5: 代码审查Agent (Week 9-10)

**目标**: 自动代码审查和报告生成

#### 功能实现
- [ ] 静态代码分析（pylint/ruff）
- [ ] LLM深度审查
- [ ] 报告生成（Markdown格式）
- [ ] 异步任务处理（Celery）
- [ ] 任务状态查询

#### API接口
- [ ] POST /api/v1/review/analyze - 发起审查
- [ ] GET /api/v1/review/result/{taskId} - 查询结果

**交付物**:
- 审查功能可用
- 生成可读的报告

---

### Phase 6: 性能优化和完善 (Week 11-12)

**目标**: 性能优化、文档完善、部署

#### 性能优化
- [ ] Redis缓存策略优化
- [ ] 数据库索引优化
- [ ] 批量处理优化
- [ ] 接口响应时间优化（<200ms）

#### 文档完善
- [ ] API接口文档完善
- [ ] 代码注释补充
- [ ] 部署文档
- [ ] 开发文档

#### 部署
- [ ] Docker镜像优化
- [ ] docker-compose生产配置
- [ ] 云平台部署（可选）
- [ ] CI/CD配置（可选）

#### 演示准备
- [ ] 演示视频录制
- [ ] PPT制作
- [ ] 技术博客撰写

**交付物**:
- 完整可演示的系统
- 完善的文档
- 部署到云平台

---

## 技术债务

### 当前已知问题
- 暂无

### 待优化项
- [ ] 服务间通信可以从HTTP升级到gRPC（性能优化）
- [ ] 分布式事务处理（目前采用补偿机制）
- [ ] 监控和告警系统
- [ ] 全链路日志追踪
- [ ] API限流和熔断

---

## 版本规划

### v0.1.0 - 项目初始化 ✅
- 基础框架搭建
- 文档创建

### v0.2.0 - 用户认证 (预计Week 4)
- 用户注册登录
- JWT认证

### v0.3.0 - 项目管理 (预计Week 6)
- 项目CRUD
- 服务间调用

### v0.4.0 - RAG问答 (预计Week 8)
- 代码索引
- 智能问答

### v0.5.0 - 代码审查 (预计Week 10)
- 自动审查
- 报告生成

### v1.0.0 - 正式版 (预计Week 12)
- 功能完整
- 文档完善
- 部署上线

---

## 贡献者

- **主要开发者**: [Your Name]
- **项目时间**: 2025-11 ~ 2026-02
- **项目目的**: Agent应用开发实习求职

---

## 参考

### 遵循的规范
- [语义化版本](https://semver.org/lang/zh-CN/)
- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)
- [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)

### 灵感来源
- Quivr - 个人知识库
- gpt-engineer - AI代码生成
- langchain-ChatGLM - 中文RAG实践

---

**最后更新**: 2025-11-15
