# Agent Service - Python微服务

基于FastAPI的智能代码助手Agent服务，提供RAG问答和代码审查功能。

## 📋 功能特性

- ✅ **健康检查**: `/api/v1/health`, `/api/v1/ready`, `/api/v1/ping`
- 🔄 **统一响应格式**: 与Java服务保持一致的JSON响应结构
- ⚡ **异步架构**: 基于FastAPI和Redis的高性能异步服务
- 📝 **结构化日志**: JSON格式日志支持（生产环境）
- 🔒 **CORS配置**: 跨域请求支持
- 🚨 **全局异常处理**: 业务异常、参数验证、未知异常

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- Redis 6.0+
- OpenAI API Key（用于LLM功能）

### 2. 安装依赖

**方式一：使用虚拟环境（推荐）**

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows Git Bash:
source venv/Scripts/activate
# Windows CMD:
venv\Scripts\activate.bat
# Windows powershell
.\venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**方式二：使用系统Python**

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑.env文件，至少需要配置：
# - OPENAI_API_KEY: OpenAI API密钥
# - REDIS_HOST: Redis主机地址（默认localhost）
```

### 4. 启动服务

```bash
# 开发模式（启用热重载）
python main.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 验证服务

访问以下URL验证服务是否正常运行：

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/health
- **Ping测试**: http://localhost:8000/api/v1/ping

## 📂 项目结构

```
agent-service/
├── main.py                 # FastAPI应用入口
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量模板
├── .env                   # 环境变量（git忽略）
├── app/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── dependencies.py    # 依赖注入
│   ├── core/              # 核心模块
│   │   ├── response.py    # 统一响应格式
│   │   └── exceptions.py  # 异常定义
│   ├── api/               # API路由
│   │   └── v1/
│   │       ├── health.py  # 健康检查接口
│   │       ├── chat.py    # 代码问答（TODO）
│   │       ├── index.py   # 代码索引（TODO）
│   │       └── review.py  # 代码审查（TODO）
│   ├── agents/            # Agent实现（TODO）
│   ├── services/          # 业务服务（TODO）
│   ├── models/            # 数据模型（TODO）
│   └── utils/             # 工具函数（TODO）
└── tests/                 # 测试代码
```

## 🛠️ 开发指南

### 代码风格

- 使用Black格式化代码
- 使用isort排序import
- 遵循PEP 8规范

```bash
# 格式化代码
black app/ main.py

# 排序import
isort app/ main.py

# 代码检查
ruff check app/ main.py
```

### 运行测试

```bash
# 运行所有测试
pytest

# 查看覆盖率
pytest --cov=app --cov-report=html
```

## 📖 API文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### 主要接口

#### 健康检查

```bash
# 完整健康检查（包含依赖组件）
curl http://localhost:8000/api/v1/health

# 就绪检查（检查必需依赖）
curl http://localhost:8000/api/v1/ready

# 快速Ping（仅检查服务响应）
curl http://localhost:8000/api/v1/ping
```

## 🔧 配置说明

所有配置通过环境变量设置，详见`.env.example`文件。

关键配置项：

| 环境变量 | 说明 | 默认值 |
|---------|------|-------|
| `DEBUG` | 调试模式 | `False` |
| `PORT` | 服务端口 | `8000` |
| `REDIS_HOST` | Redis主机 | `localhost` |
| `REDIS_PORT` | Redis端口 | `6379` |
| `OPENAI_API_KEY` | OpenAI密钥 | **必填** |
| `OPENAI_MODEL` | 使用的模型 | `gpt-4o-mini` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LOG_FORMAT` | 日志格式 | `json` |

## 🚨 故障排查

### 服务无法启动

1. 检查Redis是否运行：`redis-cli ping`
2. 检查端口是否被占用：`lsof -i:8000`（Linux/Mac）或`netstat -ano | findstr :8000`（Windows）
3. 检查日志输出确认错误信息

### Redis连接失败

- 确认Redis服务已启动
- 检查`REDIS_HOST`和`REDIS_PORT`配置
- 如果Redis需要密码，配置`REDIS_PASSWORD`

### OpenAI API错误

- 确认`OPENAI_API_KEY`正确配置
- 检查API Key额度和权限
- 如果使用代理，配置`OPENAI_API_BASE`

## 📝 待实现功能

- [ ] Phase 4: RAG问答Agent (`/api/v1/chat/ask`)
- [ ] Phase 4: 代码索引服务 (`/api/v1/index/repository`)
- [ ] Phase 5: 代码审查Agent (`/api/v1/review/analyze`)
- [ ] Phase 3: Java服务集成（项目管理调用）

## 📄 License

Code Assistant Platform - Internal Project
