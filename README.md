# 智能代码助手平台 (微服务架构)

## 项目简介

基于微服务架构的智能代码助手平台，采用 **Java Spring Boot** 处理业务逻辑，**Python FastAPI** 提供AI Agent服务，通过HTTP实现服务间通信。

## 核心特性

- 🎯 **微服务架构**: Java业务层 + Python AI层，职责清晰
- 🤖 **智能Agent**: 代码问答、代码审查、文档生成
- 🔐 **完整认证**: JWT-based用户认证和授权
- 🚀 **高性能**: Redis缓存 + 异步任务处理
- 🐳 **容器化**: Docker-compose一键部署

## 技术架构

```
┌─────────────────────────────────────┐
│         前端 (可选)                  │
└─────────────────────────────────────┘
                  ↓
           Nginx (反向代理)
                  ↓
    ┌──────────────────┬──────────────────┐
    │   Java服务        │  Python Agent     │
    │  Spring Boot     │    FastAPI        │
    │  - 用户管理      │  - 代码问答Agent  │
    │  - 项目管理      │  - 代码审查Agent  │
    │  - 任务调度      │  - RAG检索        │
    └──────────────────┴──────────────────┘
              ↓                ↓
    ┌─────────────────────────────────────┐
    │  PostgreSQL + Redis + ChromaDB      │
    └─────────────────────────────────────┘
```

## 技术栈

### Java服务
- **Spring Boot 3.2** - 核心框架
- **Spring Security** - 安全认证
- **MyBatis-Plus** - ORM框架
- **JWT** - Token认证
- **PostgreSQL** - 数据库
- **Redis** - 缓存

### Python服务
- **FastAPI** - Web框架
- **LangChain** - Agent框架
- **LlamaIndex** - RAG系统
- **ChromaDB** - 向量数据库
- **Celery** - 异步任务

### 基础设施
- **Docker & Docker-compose**
- **Nginx** - 反向代理
- **PostgreSQL 14**
- **Redis 7**

## 项目结构

```
code-assistant-platform/
├── java-service/              # Java微服务
│   ├── user-service/         # 用户服务
│   │   └── src/main/java/com/codeassistant/user/
│   │       ├── controller/   # API控制器
│   │       ├── service/      # 业务逻辑
│   │       ├── mapper/       # 数据访问
│   │       ├── entity/       # 实体类
│   │       ├── dto/          # 数据传输对象
│   │       ├── config/       # 配置类
│   │       └── security/     # 安全相关
│   └── project-service/      # 项目管理服务
│       └── src/main/java/com/codeassistant/project/
├── agent-service/            # Python Agent服务
│   ├── app/
│   │   ├── api/v1/          # API路由
│   │   ├── agents/          # Agent实现
│   │   ├── services/        # 业务逻辑
│   │   ├── models/          # 数据模型
│   │   └── core/            # 核心配置
│   └── tests/               # 测试
├── docker/                   # Docker配置
│   ├── nginx/
│   ├── postgres/
│   └── redis/
├── docs/                     # 文档
└── docker-compose.yml        # 服务编排
```

## 快速开始

### 环境要求

- JDK 17+
- Python 3.10+
- Docker & Docker-compose
- Maven 3.8+

### 一键启动（推荐）

```bash
# 1. 克隆项目
git clone <your-repo>
cd code-assistant-platform

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis、LLM API等

# 3. 启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

### 本地开发

#### Java服务

```bash
cd java-service/user-service

# 安装依赖
mvn clean install

# 运行服务
mvn spring-boot:run

# API文档: http://localhost:8080/swagger-ui.html
```

#### Python服务

```bash
cd agent-service

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn app.main:app --reload --port 8000

# API文档: http://localhost:8000/docs
```

## API文档

### Java服务API (端口8080)

- **用户认证**: `POST /api/v1/auth/register`, `/login`
- **用户管理**: `GET/PUT/DELETE /api/v1/users/{id}`
- **项目管理**: `GET/POST /api/v1/projects`

### Python Agent API (端口8000)

- **代码问答**: `POST /api/v1/chat/ask`
- **代码审查**: `POST /api/v1/review/analyze`
- **代码索引**: `POST /api/v1/index/repository`

详细API文档见各服务的Swagger/OpenAPI页面。

## 开发计划

### Phase 1: 基础框架 (Week 1-2) ✅
- [x] 项目结构搭建
- [x] Java用户服务基础
- [x] Python Agent服务基础
- [x] Docker-compose配置

### Phase 2: 核心功能 (Week 3-6)
- [ ] JWT认证实现
- [ ] 用户CRUD完善
- [ ] 项目管理功能
- [ ] RAG系统实现
- [ ] 代码问答Agent

### Phase 3: 服务集成 (Week 7-8)
- [ ] Java调用Python服务
- [ ] 统一异常处理
- [ ] Redis缓存集成
- [ ] 日志和监控

### Phase 4: 高级特性 (Week 9-10)
- [ ] 代码审查Agent
- [ ] 异步任务处理
- [ ] WebSocket实时通信
- [ ] 性能优化

### Phase 5: 部署上线 (Week 11-12)
- [ ] 生产环境配置
- [ ] CI/CD流程
- [ ] 文档完善
- [ ] 演示视频

## 学习资源

### Java Spring Boot
- [Spring Boot官方文档](https://spring.io/projects/spring-boot)
- [Spring Security教程](https://spring.io/guides/topicals/spring-security-architecture)
- 《Spring Boot实战》

### Python Agent开发
- [LangChain官方文档](https://python.langchain.com/)
- [FastAPI教程](https://fastapi.tiangolo.com/zh/)
- DeepLearning.AI - LangChain for LLM

### 微服务架构
- 《微服务设计》- Sam Newman
- 《Spring Cloud微服务实战》

## 常见问题

**Q: 为什么要拆分Java和Python服务？**
A: Java擅长处理业务逻辑和事务，Python生态更适合AI/ML任务。拆分后各司其职，便于维护和扩展。

**Q: 服务间通信性能如何？**
A: 使用HTTP REST调用，局域网延迟<10ms。后续可优化为gRPC提升性能。

**Q: 如何保证数据一致性？**
A: 使用分布式事务（Seata）或最终一致性（消息队列）。当前版本以简单为主，采用补偿机制。

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交代码
4. 发起Pull Request

## 许可证

MIT License

## 联系方式

- GitHub: [your-github]
- Email: [your-email]

---

**开发进度**: 🚧 积极开发中

**最后更新**: 2025-11
