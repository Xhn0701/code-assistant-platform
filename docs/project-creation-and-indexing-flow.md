# 项目创建和自动索引完整流程设计

## 📋 概述

本文档描述了项目创建、代码克隆/验证、自动索引的完整流程设计。

**设计目标**: 创建项目 → 克隆/验证代码路径 → 自动触发索引 → 索引完成后状态变 READY

---

## 🔄 完整流程图

```
用户创建项目
    ↓
[ProjectController.createProject]
    ↓
[ProjectService.createProject]
    ↓
1. 检查项目名称重复
    ↓
2. 保存项目到数据库 (状态: CREATED, 索引状态: PENDING)
    ↓
3. 准备项目路径 [prepareProjectPath]
    ↓
    ├─→ LOCAL 类型: 验证本地路径是否存在
    │   └─→ 成功: 返回本地路径
    │   └─→ 失败: 抛出异常
    │
    └─→ 远程仓库 (GITHUB/GITLAB/BITBUCKET):
        └─→ [GitService.cloneRepository]
            ├─→ 生成唯一目录: /tmp/code-assistant/project-{id}
            ├─→ 执行 git clone --depth 1
            └─→ 返回克隆后的本地路径
    ↓
4. 更新项目 local_path 字段
    ↓
5. 自动触发索引 [triggerAutoIndex]
    ↓
    ├─→ 更新项目状态: INDEXING
    ├─→ 更新索引状态: INDEXING
    └─→ 调用 AgentClientService.indexRepository
        └─→ POST http://agent-service:8000/api/v1/index
            {
                "projectId": 1,
                "repositoryPath": "/tmp/code-assistant/project-1",
                "indexType": "FULL"
            }
    ↓
6. Agent 服务开始异步索引
    ↓
[异步等待索引完成...]
    ↓
7. 索引完成,Agent 服务回调
    ↓
POST http://user-service:8080/api/v1/callback/index-status
    {
        "projectId": 1,
        "status": "COMPLETED",  // 或 "FAILED"
        "totalFiles": 150,
        "indexedFiles": 150,
        "language": "Java"
    }
    ↓
[CallbackController.updateIndexStatus]
    ↓
[ProjectService.handleIndexCallback]
    ↓
8. 更新项目状态:
    ├─→ 成功: status=READY, indexStatus=COMPLETED
    └─→ 失败: status=ERROR, indexStatus=FAILED
    ↓
✅ 流程完成
```

---

## 📁 新增/修改的文件

### 1. 数据库迁移
**文件**: `V4__add_local_path_to_projects.sql`
```sql
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS local_path VARCHAR(1000);
```

### 2. 实体类
**文件**: `Project.java`
```java
@TableField("local_path")
private String localPath;
```

### 3. DTO
**文件**: `CreateProjectRequest.java`
```java
private String localPath;  // 可选,支持用户指定本地路径
```

**文件**: `ProjectResponse.java`
```java
private String localPath;  // 返回给前端
```

**文件**: `IndexCallbackRequest.java` (新增)
```java
// Agent 服务回调使用
private Long projectId;
private String status;  // COMPLETED / FAILED
private Integer totalFiles;
private Integer indexedFiles;
private String language;
private String errorMessage;
```

### 4. 服务类
**文件**: `GitService.java` (新增)
- `cloneRepository()`: 克隆 Git 仓库到本地
- `pullRepository()`: 更新已存在的仓库
- `validateLocalPath()`: 验证本地路径是否有效
- `executeGitClone()`: 执行 git clone 命令
- `extractRepoName()`: 从 URL 提取仓库名

**文件**: `ProjectService.java` (重要修改)
- `createProject()`: 重写完整流程
  - `prepareProjectPath()`: 准备项目路径
  - `triggerAutoIndex()`: 自动触发索引
- `handleIndexCallback()`: 处理索引回调,更新状态

### 5. 控制器
**文件**: `CallbackController.java` (新增)
- `POST /api/v1/callback/index-status`: 接收 Agent 服务的索引完成回调

### 6. 配置文件
**文件**: `application.yml`
```yaml
project:
  repository:
    base-path: /tmp/code-assistant
    clone-timeout: 300
```

---

## 🎯 核心设计要点

### 1. 仓库路径处理

#### LOCAL 类型项目
```java
{
  "name": "My Local Project",
  "repositoryType": "LOCAL",
  "localPath": "/home/user/code/my-project"  // 必填
}
```
- **要求**: 必须提供 `localPath`
- **验证**: 检查路径是否存在且是目录
- **索引**: 直接使用该路径进行索引

#### 远程仓库项目 (GITHUB/GITLAB/BITBUCKET)
```java
{
  "name": "Spring Boot Demo",
  "repositoryUrl": "https://github.com/user/spring-boot-demo.git",
  "repositoryType": "GITHUB",
  "localPath": null  // 可选
}
```
- **自动克隆**: 如果未提供 `localPath`,自动克隆到 `/tmp/code-assistant/project-{id}`
- **用户指定**: 如果提供 `localPath`,克隆到指定位置(未来功能)
- **浅克隆**: 使用 `git clone --depth 1` 节省空间和时间

### 2. 状态流转

```
项目状态 (status):
CREATED → INDEXING → READY (成功)
                  → ERROR (失败)

索引状态 (index_status):
PENDING → INDEXING → COMPLETED (成功)
                   → FAILED (失败)
```

### 3. 异步索引设计

**为什么是异步?**
- 索引大型项目可能需要几分钟甚至更长时间
- 不能阻塞 HTTP 请求
- 使用 Celery 异步任务队列处理

**回调机制**:
1. Java 服务调用 Agent 服务 `/api/v1/index` 接口
2. Agent 服务立即返回 `taskId`
3. Agent 服务在后台异步索引
4. 索引完成后,Agent 服务回调 Java 服务 `/api/v1/callback/index-status`
5. Java 服务更新项目状态

---

## 🔌 API 接口

### 1. 创建项目 (已有接口,行为变更)
```http
POST /api/v1/projects
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description",
  "repositoryUrl": "https://github.com/user/repo.git",
  "repositoryType": "GITHUB",
  "localPath": null
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "My Project",
    "repositoryUrl": "https://github.com/user/repo.git",
    "repositoryType": "GITHUB",
    "localPath": "/tmp/code-assistant/project-1",
    "status": "INDEXING",        // 注意: 不再是 CREATED
    "indexStatus": "INDEXING",   // 注意: 不再是 PENDING
    "totalFiles": 0,
    "indexedFiles": 0
  }
}
```

### 2. 索引状态回调 (新增,Agent 服务调用)
```http
POST /api/v1/callback/index-status
Content-Type: application/json

{
  "projectId": 1,
  "status": "COMPLETED",
  "totalFiles": 150,
  "indexedFiles": 150,
  "language": "Java",
  "taskId": "abc-123-xyz"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success"
}
```

---

## 🛠️ Agent 服务需要实现的部分

### 1. 索引完成后回调
在 `index_repository` 任务完成后,调用 Java 服务的回调接口:

```python
# agent-service/app/tasks/index_task.py

@celery_app.task(bind=True)
def index_repository(self, project_id: int, repository_path: str):
    try:
        # ... 执行索引逻辑 ...

        # 索引成功,回调 Java 服务
        callback_data = {
            "projectId": project_id,
            "status": "COMPLETED",
            "totalFiles": total_files,
            "indexedFiles": indexed_files,
            "language": detected_language,
            "taskId": self.request.id
        }

        java_service_url = os.getenv("JAVA_SERVICE_URL", "http://localhost:8080")
        requests.post(
            f"{java_service_url}/api/v1/callback/index-status",
            json=callback_data,
            timeout=10
        )

    except Exception as e:
        # 索引失败,回调 Java 服务
        callback_data = {
            "projectId": project_id,
            "status": "FAILED",
            "errorMessage": str(e),
            "taskId": self.request.id
        }

        requests.post(
            f"{java_service_url}/api/v1/callback/index-status",
            json=callback_data,
            timeout=10
        )
```

### 2. 环境变量配置
在 Agent 服务的 `.env` 或 `docker-compose.yml` 中添加:
```bash
JAVA_SERVICE_URL=http://user-service:8080
```

---

## 🧪 测试流程

### 测试场景 1: GitHub 仓库项目

1. **创建项目**:
```bash
curl -X POST http://localhost:8080/api/v1/projects \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "repositoryUrl": "https://github.com/spring-projects/spring-boot.git",
    "repositoryType": "GITHUB"
  }'
```

2. **验证克隆**:
```bash
# 检查目录是否存在
ls -la /tmp/code-assistant/project-1

# 检查 git 仓库
cd /tmp/code-assistant/project-1 && git log -1
```

3. **验证索引状态**:
```bash
curl http://localhost:8080/api/v1/projects/1 \
  -H "Authorization: Bearer {token}"

# 应该看到 status: INDEXING, indexStatus: INDEXING
```

4. **等待索引完成** (模拟回调):
```bash
curl -X POST http://localhost:8080/api/v1/callback/index-status \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 1,
    "status": "COMPLETED",
    "totalFiles": 150,
    "indexedFiles": 150,
    "language": "Java"
  }'
```

5. **再次查询项目**:
```bash
curl http://localhost:8080/api/v1/projects/1 \
  -H "Authorization: Bearer {token}"

# 应该看到 status: READY, indexStatus: COMPLETED
```

### 测试场景 2: 本地项目

```bash
# 创建测试目录
mkdir -p /tmp/test-local-project
echo "console.log('test')" > /tmp/test-local-project/index.js

# 创建项目
curl -X POST http://localhost:8080/api/v1/projects \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Local Test Project",
    "repositoryType": "LOCAL",
    "localPath": "/tmp/test-local-project"
  }'
```

---

## ⚠️ 注意事项

### 1. Git 命令依赖
- 服务器必须安装 `git` 命令
- Docker 镜像需要包含 git: `RUN apt-get install -y git`

### 2. 磁盘空间
- 大型仓库可能占用大量空间
- 建议定期清理未使用的项目克隆目录
- 可以添加定时任务清理已删除项目的目录

### 3. 网络访问
- 克隆 GitHub 仓库需要网络访问
- 可能需要配置代理: `git config --global http.proxy`
- 私有仓库需要配置 SSH 密钥或 Personal Access Token

### 4. 超时设置
- 默认 clone 超时 300 秒 (5 分钟)
- 大型仓库可能需要更长时间
- 可通过环境变量 `PROJECT_CLONE_TIMEOUT` 调整

### 5. 安全性
- 回调接口目前无认证,建议添加签名验证
- 本地路径需要验证,防止路径穿越攻击
- Git clone 需要防止恶意 URL (SSRF)

---

## 🚀 未来优化

### 1. 支持私有仓库
- 添加 SSH 密钥管理
- 支持 GitHub Personal Access Token
- 支持 GitLab Deploy Token

### 2. 增量索引
- 定期 `git pull` 更新代码
- 只索引变更的文件
- 支持 webhook 触发更新

### 3. 克隆进度反馈
- 实时显示克隆进度
- WebSocket 推送进度信息
- 前端进度条显示

### 4. 缓存机制
- 相同仓库的多个项目共享克隆
- 使用 Git worktree 或 symbolic link

### 5. 错误重试
- 克隆失败自动重试
- 索引失败自动重试
- 指数退避策略

---

## 📊 数据库 Schema 变更

```sql
-- V4__add_local_path_to_projects.sql

ALTER TABLE projects
ADD COLUMN IF NOT EXISTS local_path VARCHAR(1000);

COMMENT ON COLUMN projects.local_path IS '项目本地路径 - 克隆或指定的代码路径';
```

---

## 🔗 相关文档

- [PROJECTWIKI.md](../PROJECTWIKI.md) - 项目技术文档
- [CHANGELOG.md](../CHANGELOG.md) - 版本变更记录
- [Phase 4 RAG Agent 设计](./phase4-rag-agent-design.md) - RAG Agent 详细设计

---

**文档版本**: v1.0.0
**创建时间**: 2025-11-21
**作者**: Claude Code AI Assistant
