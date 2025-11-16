# 开发路线图 (Development Roadmap)

本文档详细规划了项目的开发顺序、每个功能的前置条件、完成标准和验收标准。

---

## 📊 总体进度概览

```
Phase 1: 基础框架搭建        [=====>................] 25%  (Week 1-2)
Phase 2: 用户认证系统        [......................] 0%   (Week 3-4)
Phase 3: 项目管理功能        [......................] 0%   (Week 5-6)
Phase 4: RAG问答Agent       [......................] 0%   (Week 7-8)
Phase 5: 代码审查Agent      [......................] 0%   (Week 9-10)
Phase 6: 性能优化与部署      [......................] 0%   (Week 11-12)
```

**当前阶段**: Phase 1 - 基础框架搭建
**当前任务**: Task 1.2 - Java服务基础代码

---

## 🎯 开发原则

### 1. 按依赖顺序开发
- 先底层后上层（数据库 → 服务层 → API层）
- 先基础后高级（基本CRUD → 复杂业务逻辑）
- 先Java后Python（业务逻辑先跑通，再集成AI）

### 2. 每个任务的完成标准
- ✅ 代码编写完成
- ✅ 单元测试通过
- ✅ 接口测试通过（Postman/Swagger）
- ✅ 文档已更新（CHANGELOG + PROJECTWIKI）
- ✅ 代码已提交（Git commit）

### 3. 里程碑验收标准
- 每个Phase结束时，整个服务可以运行
- 核心功能可以通过API测试
- 文档与代码同步

---

## Phase 1: 基础框架搭建 (Week 1-2)

**目标**: 搭建完整的开发环境和项目框架，所有服务可以启动并访问API文档。

**总体完成标准**:
- Java服务启动成功，可以访问Swagger文档
- Python服务启动成功，可以访问FastAPI文档
- PostgreSQL和Redis连接正常
- Docker-compose可以一键启动所有服务

---

### Task 1.1: 项目初始化 ✅

**状态**: 已完成

**完成内容**:
- ✅ 项目目录结构
- ✅ README.md
- ✅ PROJECTWIKI.md
- ✅ CHANGELOG.md
- ✅ CLAUDE.md
- ✅ DEVELOPMENT_ROADMAP.md (本文档)
- ✅ .gitignore
- ✅ .env.example

---

### Task 1.2: Java用户服务基础代码 🔄

**前置条件**:
- ✅ Task 1.1 已完成
- ✅ JDK 17+ 已安装
- ✅ Maven 3.8+ 已安装
- ✅ IDE (IntelliJ IDEA) 已配置

**开发步骤**:

#### Step 1: 启动类和基础配置
**文件清单**:
```
user-service/src/main/java/com/codeassistant/user/
├── UserServiceApplication.java          # 启动类
├── config/
│   ├── RedisConfig.java                # Redis配置
│   ├── SwaggerConfig.java              # Swagger配置
│   └── CorsConfig.java                 # 跨域配置
└── common/
    ├── Result.java                     # 统一返回格式
    ├── ResultCode.java                 # 返回码枚举
    └── GlobalExceptionHandler.java     # 全局异常处理
```

**代码要求**:
- UserServiceApplication.java
  - 包含 @SpringBootApplication 注解
  - 包含 @MapperScan 注解扫描Mapper
  - 包含 @EnableCaching 启用缓存
  - main方法启动应用

- Result.java 统一返回格式
  ```java
  {
    "code": 200,
    "message": "success",
    "data": { ... },
    "timestamp": 1234567890
  }
  ```

- GlobalExceptionHandler.java
  - 处理参数校验异常 (MethodArgumentNotValidException)
  - 处理业务异常 (BusinessException)
  - 处理系统异常 (Exception)

**完成标准**:
- [ ] 所有文件创建完成
- [ ] 代码无编译错误
- [ ] 启动类可以运行（无报错）
- [ ] Swagger可以访问: http://localhost:8080/swagger-ui.html
- [ ] 健康检查接口返回正常: http://localhost:8080/actuator/health

**验收测试**:
```bash
# 1. 编译项目
cd java-service/user-service
mvn clean compile

# 2. 启动服务
mvn spring-boot:run

# 3. 测试Swagger
curl http://localhost:8080/swagger-ui.html
# 预期: 返回HTML页面

# 4. 测试健康检查
curl http://localhost:8080/actuator/health
# 预期: {"status":"UP"}
```

**文档更新**:
- [ ] CHANGELOG.md添加: "Java用户服务基础框架搭建完成"
- [ ] PROJECTWIKI.md更新: 确认技术栈版本信息

**预估时间**: 2-3小时

---

#### Step 2: 数据库连接测试
**文件清单**:
```
user-service/src/main/java/com/codeassistant/user/
├── entity/
│   └── User.java                       # 用户实体类（简化版）
├── mapper/
│   └── UserMapper.java                 # MyBatis Mapper
└── controller/
    └── HealthController.java           # 健康检查控制器
```

```sql
resources/db/migration/
└── V1__create_users_table.sql         # 数据库初始化脚本
```

**代码要求**:
- User.java
  ```java
  @Data
  @TableName("users")
  public class User {
      @TableId(type = IdType.AUTO)
      private Long id;
      private String username;
      private String email;
      private LocalDateTime createdAt;
  }
  ```

- UserMapper.java
  ```java
  @Mapper
  public interface UserMapper extends BaseMapper<User> {
  }
  ```

- V1__create_users_table.sql
  ```sql
  CREATE TABLE users (
      id BIGSERIAL PRIMARY KEY,
      username VARCHAR(50) UNIQUE NOT NULL,
      email VARCHAR(100) UNIQUE NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

**完成标准**:
- [ ] PostgreSQL数据库已启动
- [ ] users表创建成功
- [ ] 可以通过Mapper查询数据库
- [ ] HealthController可以返回数据库连接状态

**验收测试**:
```bash
# 1. 启动PostgreSQL (Docker)
docker run -d \
  --name postgres \
  -e POSTGRES_DB=code_assistant \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres123 \
  -p 5432:5432 \
  postgres:14

# 2. 连接数据库执行初始化脚本
psql -h localhost -U postgres -d code_assistant -f resources/db/migration/V1__create_users_table.sql

# 3. 启动Java服务测试
mvn spring-boot:run

# 4. 测试数据库连接
curl http://localhost:8080/api/health/db
# 预期: {"status":"connected", "database":"code_assistant"}
```

**文档更新**:
- [ ] CHANGELOG.md添加: "PostgreSQL数据库集成完成"
- [ ] PROJECTWIKI.md更新: 数据库设计章节添加users表

**预估时间**: 2小时

---

#### Step 3: Redis连接测试
**文件清单**:
```
user-service/src/main/java/com/codeassistant/user/
└── controller/
    └── HealthController.java           # 扩展Redis检查
```

**代码要求**:
- RedisTemplate可以正常使用
- 可以set和get测试数据

**完成标准**:
- [ ] Redis已启动
- [ ] RedisTemplate注入成功
- [ ] 可以写入和读取缓存数据

**验收测试**:
```bash
# 1. 启动Redis
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7

# 2. 测试Redis连接
curl http://localhost:8080/api/health/redis
# 预期: {"status":"connected"}

# 3. 测试缓存读写
curl -X POST http://localhost:8080/api/health/cache/test
# 预期: {"success": true, "cached": "test-value"}
```

**文档更新**:
- [ ] CHANGELOG.md添加: "Redis缓存集成完成"

**预估时间**: 1小时

---

### Task 1.3: Python Agent服务基础框架 ⏳

**前置条件**:
- ✅ Task 1.1 已完成
- ✅ Python 3.10+ 已安装
- ✅ pip 已配置

**开发步骤**:

#### Step 1: 创建Python虚拟环境和依赖配置
**文件清单**:
```
agent-service/
├── requirements.txt                    # Python依赖
├── requirements-dev.txt                # 开发依赖
├── .python-version                     # Python版本
└── README.md                          # Python服务说明
```

**requirements.txt内容**:
```txt
# Web框架
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# LLM和Agent
langchain==0.1.0
langchain-community==0.0.10
langchain-openai==0.0.2
openai==1.6.1

# 向量数据库
chromadb==0.4.18

# 数据库
psycopg2-binary==2.9.9
redis==5.0.1

# 工具
python-dotenv==1.0.0
python-multipart==0.0.6
httpx==0.25.2

# 任务队列
celery==5.3.4
```

**完成标准**:
- [ ] requirements.txt创建完成
- [ ] 虚拟环境创建成功
- [ ] 所有依赖安装成功（无错误）

**验收测试**:
```bash
# 1. 创建虚拟环境
cd agent-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证安装
python -c "import fastapi; import langchain; print('Dependencies OK')"
# 预期: Dependencies OK
```

**预估时间**: 0.5小时

---

#### Step 2: FastAPI基础代码
**文件清单**:
```
agent-service/app/
├── main.py                            # FastAPI入口
├── core/
│   ├── __init__.py
│   ├── config.py                      # 配置管理
│   └── dependencies.py                # 依赖注入
├── api/
│   └── v1/
│       ├── __init__.py
│       └── health.py                  # 健康检查接口
└── models/
    ├── __init__.py
    └── common.py                      # 通用数据模型
```

**代码要求**:
- main.py
  ```python
  from fastapi import FastAPI
  from app.api.v1 import health

  app = FastAPI(
      title="Code Assistant Agent Service",
      version="0.1.0"
  )

  app.include_router(health.router, prefix="/api/v1")

  @app.get("/")
  def root():
      return {"message": "Agent Service is running"}
  ```

- config.py
  ```python
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      # 应用配置
      app_name: str = "Agent Service"
      debug: bool = True

      # LLM配置
      openai_api_key: str
      openai_model: str = "gpt-4-turbo-preview"

      # 数据库配置
      postgres_url: str
      redis_url: str

      class Config:
          env_file = ".env"
  ```

- common.py
  ```python
  from pydantic import BaseModel
  from typing import Any, Optional

  class Response(BaseModel):
      code: int = 200
      message: str = "success"
      data: Optional[Any] = None
  ```

**完成标准**:
- [ ] 所有文件创建完成
- [ ] FastAPI应用可以启动
- [ ] 可以访问API文档: http://localhost:8000/docs
- [ ] 健康检查接口正常

**验收测试**:
```bash
# 1. 启动服务
cd agent-service
uvicorn app.main:app --reload --port 8000

# 2. 测试根路径
curl http://localhost:8000/
# 预期: {"message": "Agent Service is running"}

# 3. 测试健康检查
curl http://localhost:8000/api/v1/health
# 预期: {"status": "healthy", "version": "0.1.0"}

# 4. 访问API文档
curl http://localhost:8000/docs
# 预期: 返回HTML页面
```

**文档更新**:
- [ ] CHANGELOG.md添加: "Python Agent服务基础框架搭建完成"
- [ ] PROJECTWIKI.md更新: Python服务启动说明

**预估时间**: 2小时

---

### Task 1.4: Docker-compose服务编排 ⏳

**前置条件**:
- ✅ Task 1.2 已完成（Java服务可以启动）
- ✅ Task 1.3 已完成（Python服务可以启动）
- ✅ Docker已安装

**开发步骤**:

#### Step 1: 创建docker-compose.yml
**文件清单**:
```
code-assistant-platform/
├── docker-compose.yml                 # 服务编排
├── .env                               # 环境变量（从.env.example复制）
└── docker/
    ├── postgres/
    │   └── init.sql                   # 数据库初始化脚本
    ├── nginx/
    │   └── nginx.conf                 # Nginx配置
    └── java/
        └── Dockerfile                 # Java服务镜像
```

**docker-compose.yml要求**:
```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:14
    container_name: code-assistant-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "${POSTGRES_PORT}:5432"
    volumes:
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
      - postgres_data:/var/lib/postgresql/data
    networks:
      - code-assistant-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: code-assistant-redis
    ports:
      - "${REDIS_PORT}:6379"
    volumes:
      - redis_data:/data
    networks:
      - code-assistant-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Java用户服务（开发阶段先不容器化，本地运行）
  # user-service:
  #   build:
  #     context: ./java-service/user-service
  #     dockerfile: Dockerfile
  #   ports:
  #     - "8080:8080"
  #   depends_on:
  #     - postgres
  #     - redis
  #   networks:
  #     - code-assistant-network

  # Python Agent服务（开发阶段先不容器化，本地运行）
  # agent-service:
  #   build:
  #     context: ./agent-service
  #     dockerfile: Dockerfile
  #   ports:
  #     - "8000:8000"
  #   depends_on:
  #     - postgres
  #     - redis
  #   networks:
  #     - code-assistant-network

volumes:
  postgres_data:
  redis_data:

networks:
  code-assistant-network:
    driver: bridge
```

**完成标准**:
- [ ] docker-compose.yml创建完成
- [ ] .env文件配置正确
- [ ] PostgreSQL和Redis可以启动
- [ ] 数据库初始化脚本执行成功
- [ ] Java和Python服务可以连接到容器化的数据库

**验收测试**:
```bash
# 1. 启动基础服务
docker-compose up -d postgres redis

# 2. 检查服务状态
docker-compose ps
# 预期: postgres和redis都是Up状态

# 3. 测试数据库连接
docker-compose exec postgres psql -U postgres -d code_assistant -c "SELECT 1;"
# 预期: 返回1

# 4. 测试Redis连接
docker-compose exec redis redis-cli ping
# 预期: PONG

# 5. 启动Java服务（本地）
cd java-service/user-service
mvn spring-boot:run
# 预期: 连接到Docker中的PostgreSQL和Redis

# 6. 启动Python服务（本地）
cd agent-service
uvicorn app.main:app --reload
# 预期: 可以连接到Docker中的数据库
```

**文档更新**:
- [ ] CHANGELOG.md添加: "Docker-compose服务编排配置完成"
- [ ] PROJECTWIKI.md更新: 部署指南章节
- [ ] README.md更新: 快速开始章节

**预估时间**: 2小时

---

### Task 1.5: Phase 1 整体验收 ⏳

**验收标准**:

#### 1. 环境检查
- [ ] JDK 17+ 已安装
- [ ] Maven 3.8+ 已安装
- [ ] Python 3.10+ 已安装
- [ ] Docker已安装并运行
- [ ] IDE配置完成

#### 2. 服务启动检查
```bash
# 启动所有服务
docker-compose up -d postgres redis
cd java-service/user-service && mvn spring-boot:run &
cd agent-service && uvicorn app.main:app --reload &

# 等待30秒后检查
sleep 30
```

#### 3. 接口测试
```bash
# Java服务
curl http://localhost:8080/swagger-ui.html  # 返回Swagger页面
curl http://localhost:8080/api/health       # 返回{"status":"UP"}
curl http://localhost:8080/api/health/db    # 返回数据库连接正常
curl http://localhost:8080/api/health/redis # 返回Redis连接正常

# Python服务
curl http://localhost:8000/docs             # 返回FastAPI文档
curl http://localhost:8000/                 # 返回欢迎信息
curl http://localhost:8000/api/v1/health    # 返回健康状态
```

#### 4. 数据库检查
```bash
# 检查表是否创建
docker-compose exec postgres psql -U postgres -d code_assistant -c "\dt"
# 预期: 显示users表

# 检查可以插入数据
docker-compose exec postgres psql -U postgres -d code_assistant -c "
INSERT INTO users (username, email) VALUES ('test', 'test@example.com');
SELECT * FROM users;
"
# 预期: 返回刚插入的数据
```

#### 5. 文档检查
- [ ] README.md完整且可以按照步骤启动
- [ ] PROJECTWIKI.md架构图与实际一致
- [ ] CHANGELOG.md记录了所有变更
- [ ] 所有代码有基本注释

#### 6. Git提交检查
```bash
git status
# 预期: 所有文件已提交或在.gitignore中

git log --oneline -10
# 预期: 有清晰的提交历史
```

**Phase 1 完成标志**:
- ✅ 所有服务可以启动
- ✅ API文档可以访问
- ✅ 数据库和Redis连接正常
- ✅ 文档与代码同步
- ✅ 代码已提交到Git

**预估总时间**: Week 1-2 (10-15小时)

---

## Phase 2: 用户认证系统 (Week 3-4)

**目标**: 实现完整的用户注册、登录、JWT认证和权限验证功能。

**总体完成标准**:
- 用户可以通过API注册账号
- 用户可以登录并获得JWT Token
- 受保护的接口需要Token才能访问
- Token可以刷新
- 密码采用BCrypt加密
- Redis缓存用户会话

---

### Task 2.1: 用户实体和数据访问层 ⏳

**前置条件**:
- ✅ Phase 1 已完成
- ✅ PostgreSQL和Redis运行正常

**开发步骤**:

#### Step 1: 完善User实体类
**文件**: `user-service/src/main/java/com/codeassistant/user/entity/User.java`

**代码要求**:
```java
@Data
@TableName("users")
public class User {
    @TableId(type = IdType.AUTO)
    private Long id;

    @TableField("username")
    private String username;

    @TableField("email")
    private String email;

    @TableField("password")
    private String password;  // BCrypt加密后的密码

    @TableField("avatar_url")
    private String avatarUrl;

    @TableField("role")
    private String role;  // USER, ADMIN

    @TableField("status")
    private String status;  // ACTIVE, BANNED

    @TableField("created_at")
    private LocalDateTime createdAt;

    @TableField("updated_at")
    private LocalDateTime updatedAt;

    @TableLogic
    @TableField("deleted")
    private Integer deleted;  // 0-未删除, 1-已删除
}
```

**完成标准**:
- [ ] 实体类包含所有必要字段
- [ ] 使用MyBatis-Plus注解
- [ ] 支持逻辑删除
- [ ] 自动填充创建时间和更新时间

---

#### Step 2: 创建数据库迁移脚本
**文件**: `user-service/src/main/resources/db/migration/V2__alter_users_table.sql`

**SQL要求**:
```sql
-- 添加缺失字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'USER';
ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE';
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted SMALLINT NOT NULL DEFAULT 0;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username) WHERE deleted = 0;
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE deleted = 0;
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- 添加注释
COMMENT ON COLUMN users.role IS '用户角色: USER-普通用户, ADMIN-管理员';
COMMENT ON COLUMN users.status IS '用户状态: ACTIVE-活跃, BANNED-封禁';
COMMENT ON COLUMN users.deleted IS '逻辑删除标志: 0-未删除, 1-已删除';
```

**完成标准**:
- [ ] SQL脚本可以成功执行
- [ ] 所有字段添加成功
- [ ] 索引创建成功
- [ ] 无数据丢失

**验收测试**:
```bash
# 执行迁移脚本
docker-compose exec postgres psql -U postgres -d code_assistant -f /docker-entrypoint-initdb.d/V2__alter_users_table.sql

# 检查表结构
docker-compose exec postgres psql -U postgres -d code_assistant -c "\d users"
# 预期: 显示所有字段和索引
```

---

#### Step 3: 扩展UserMapper
**文件**: `user-service/src/main/java/com/codeassistant/user/mapper/UserMapper.java`

**代码要求**:
```java
@Mapper
public interface UserMapper extends BaseMapper<User> {

    /**
     * 根据用户名查询用户（包括密码）
     */
    @Select("SELECT * FROM users WHERE username = #{username} AND deleted = 0")
    User findByUsername(@Param("username") String username);

    /**
     * 根据邮箱查询用户
     */
    @Select("SELECT * FROM users WHERE email = #{email} AND deleted = 0")
    User findByEmail(@Param("email") String email);

    /**
     * 检查用户名是否存在
     */
    @Select("SELECT COUNT(*) FROM users WHERE username = #{username} AND deleted = 0")
    int countByUsername(@Param("username") String username);

    /**
     * 检查邮箱是否存在
     */
    @Select("SELECT COUNT(*) FROM users WHERE email = #{email} AND deleted = 0")
    int countByEmail(@Param("email") String email);
}
```

**完成标准**:
- [ ] Mapper接口定义完成
- [ ] SQL语句正确
- [ ] 包含逻辑删除条件

---

### Task 2.2: DTO和校验 ⏳

**前置条件**:
- ✅ Task 2.1 已完成

**开发步骤**:

#### Step 1: 创建请求DTO
**文件清单**:
```
user-service/src/main/java/com/codeassistant/user/dto/
├── RegisterRequest.java               # 注册请求
├── LoginRequest.java                  # 登录请求
├── UserUpdateRequest.java             # 用户更新请求
└── PasswordChangeRequest.java         # 修改密码请求
```

**RegisterRequest.java**:
```java
@Data
public class RegisterRequest {

    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20之间")
    @Pattern(regexp = "^[a-zA-Z0-9_]+$", message = "用户名只能包含字母、数字和下划线")
    private String username;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    @NotBlank(message = "密码不能为空")
    @Size(min = 8, max = 20, message = "密码长度必须在8-20之间")
    @Pattern(regexp = "^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d@$!%*#?&]+$",
             message = "密码必须包含字母和数字")
    private String password;
}
```

**LoginRequest.java**:
```java
@Data
public class LoginRequest {

    @NotBlank(message = "用户名或邮箱不能为空")
    private String usernameOrEmail;

    @NotBlank(message = "密码不能为空")
    private String password;
}
```

**完成标准**:
- [ ] 所有DTO类创建完成
- [ ] 包含完整的校验注解
- [ ] 错误提示信息清晰

---

#### Step 2: 创建响应DTO
**文件清单**:
```
user-service/src/main/java/com/codeassistant/user/dto/
├── UserResponse.java                  # 用户信息响应
├── LoginResponse.java                 # 登录响应
└── TokenResponse.java                 # Token响应
```

**UserResponse.java**:
```java
@Data
public class UserResponse {
    private Long id;
    private String username;
    private String email;
    private String avatarUrl;
    private String role;
    private LocalDateTime createdAt;

    // 从User实体转换
    public static UserResponse fromUser(User user) {
        UserResponse response = new UserResponse();
        response.setId(user.getId());
        response.setUsername(user.getUsername());
        response.setEmail(user.getEmail());
        response.setAvatarUrl(user.getAvatarUrl());
        response.setRole(user.getRole());
        response.setCreatedAt(user.getCreatedAt());
        return response;
    }
}
```

**LoginResponse.java**:
```java
@Data
public class LoginResponse {
    private String accessToken;
    private String refreshToken;
    private Long expiresIn;  // 秒
    private UserResponse user;
}
```

**完成标准**:
- [ ] 所有响应DTO创建完成
- [ ] 不包含敏感信息（如密码）
- [ ] 包含必要的转换方法

---

### Task 2.3: JWT工具类和Security配置 ⏳

**前置条件**:
- ✅ Task 2.2 已完成

**开发步骤**:

#### Step 1: JWT Token Provider
**文件**: `user-service/src/main/java/com/codeassistant/user/security/JwtTokenProvider.java`

**代码要求**:
```java
@Component
public class JwtTokenProvider {

    @Value("${jwt.secret}")
    private String jwtSecret;

    @Value("${jwt.expiration}")
    private long jwtExpiration;

    @Value("${jwt.refresh-expiration}")
    private long refreshExpiration;

    /**
     * 生成Access Token
     */
    public String generateAccessToken(User user) {
        // 实现Token生成逻辑
    }

    /**
     * 生成Refresh Token
     */
    public String generateRefreshToken(User user) {
        // 实现Refresh Token生成
    }

    /**
     * 从Token中提取用户名
     */
    public String getUsernameFromToken(String token) {
        // 解析Token
    }

    /**
     * 验证Token
     */
    public boolean validateToken(String token) {
        // 验证Token有效性
    }
}
```

**完成标准**:
- [ ] Token生成功能完成
- [ ] Token解析功能完成
- [ ] Token验证功能完成
- [ ] 异常处理完善

---

#### Step 2: JWT认证过滤器
**文件**: `user-service/src/main/java/com/codeassistant/user/security/JwtAuthenticationFilter.java`

**代码要求**:
```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) {
        try {
            // 1. 从Header中提取Token
            String jwt = getJwtFromRequest(request);

            // 2. 验证Token
            if (StringUtils.hasText(jwt) && jwtTokenProvider.validateToken(jwt)) {
                // 3. 获取用户名
                String username = jwtTokenProvider.getUsernameFromToken(jwt);

                // 4. 加载用户详情
                UserDetails userDetails = userDetailsService.loadUserByUsername(username);

                // 5. 设置认证信息到SecurityContext
                UsernamePasswordAuthenticationToken authentication =
                    new UsernamePasswordAuthenticationToken(
                        userDetails, null, userDetails.getAuthorities());
                SecurityContextHolder.getContext().setAuthentication(authentication);
            }
        } catch (Exception ex) {
            logger.error("Could not set user authentication in security context", ex);
        }

        filterChain.doFilter(request, response);
    }

    private String getJwtFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

**完成标准**:
- [ ] 过滤器可以提取Token
- [ ] Token验证逻辑正确
- [ ] 认证信息正确设置到SecurityContext
- [ ] 异常处理完善

---

#### Step 3: Security配置
**文件**: `user-service/src/main/java/com/codeassistant/user/security/SecurityConfig.java`

**代码要求**:
```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Autowired
    private JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                // 公开接口
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/api/health/**").permitAll()
                .requestMatchers("/swagger-ui/**", "/api-docs/**").permitAll()
                // 其他接口需要认证
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter,
                           UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration authConfig) throws Exception {
        return authConfig.getAuthenticationManager();
    }
}
```

**完成标准**:
- [ ] Security配置正确
- [ ] 公开接口无需认证
- [ ] 受保护接口需要Token
- [ ] BCrypt密码加密器配置

---

### Task 2.4: 认证服务实现 ⏳

**前置条件**:
- ✅ Task 2.3 已完成

**开发步骤**:

#### Step 1: AuthService实现
**文件**: `user-service/src/main/java/com/codeassistant/user/service/impl/AuthServiceImpl.java`

**代码要求**:
```java
@Service
public class AuthServiceImpl implements AuthService {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    /**
     * 用户注册
     */
    @Override
    @Transactional
    public UserResponse register(RegisterRequest request) {
        // 1. 检查用户名是否存在
        if (userMapper.countByUsername(request.getUsername()) > 0) {
            throw new BusinessException(ResultCode.USERNAME_ALREADY_EXISTS);
        }

        // 2. 检查邮箱是否存在
        if (userMapper.countByEmail(request.getEmail()) > 0) {
            throw new BusinessException(ResultCode.EMAIL_ALREADY_EXISTS);
        }

        // 3. 创建用户
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setRole("USER");
        user.setStatus("ACTIVE");
        user.setCreatedAt(LocalDateTime.now());
        user.setUpdatedAt(LocalDateTime.now());

        userMapper.insert(user);

        return UserResponse.fromUser(user);
    }

    /**
     * 用户登录
     */
    @Override
    public LoginResponse login(LoginRequest request) {
        // 1. 查找用户（支持用户名或邮箱登录）
        User user = findUserByUsernameOrEmail(request.getUsernameOrEmail());
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }

        // 2. 验证密码
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException(ResultCode.INVALID_PASSWORD);
        }

        // 3. 检查用户状态
        if ("BANNED".equals(user.getStatus())) {
            throw new BusinessException(ResultCode.USER_BANNED);
        }

        // 4. 生成Token
        String accessToken = jwtTokenProvider.generateAccessToken(user);
        String refreshToken = jwtTokenProvider.generateRefreshToken(user);

        // 5. 缓存用户信息到Redis
        String cacheKey = "user:session:" + user.getId();
        redisTemplate.opsForValue().set(cacheKey, user, 24, TimeUnit.HOURS);

        // 6. 构造响应
        LoginResponse response = new LoginResponse();
        response.setAccessToken(accessToken);
        response.setRefreshToken(refreshToken);
        response.setExpiresIn(jwtExpiration / 1000);
        response.setUser(UserResponse.fromUser(user));

        return response;
    }

    /**
     * 刷新Token
     */
    @Override
    public TokenResponse refreshToken(String refreshToken) {
        // 1. 验证Refresh Token
        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new BusinessException(ResultCode.INVALID_TOKEN);
        }

        // 2. 提取用户信息
        String username = jwtTokenProvider.getUsernameFromToken(refreshToken);
        User user = userMapper.findByUsername(username);

        // 3. 生成新的Access Token
        String newAccessToken = jwtTokenProvider.generateAccessToken(user);

        TokenResponse response = new TokenResponse();
        response.setAccessToken(newAccessToken);
        response.setExpiresIn(jwtExpiration / 1000);

        return response;
    }

    private User findUserByUsernameOrEmail(String usernameOrEmail) {
        // 先尝试用户名
        User user = userMapper.findByUsername(usernameOrEmail);
        if (user != null) {
            return user;
        }
        // 再尝试邮箱
        return userMapper.findByEmail(usernameOrEmail);
    }
}
```

**完成标准**:
- [ ] 注册功能完成（用户名/邮箱唯一性检查）
- [ ] 登录功能完成（支持用户名和邮箱）
- [ ] Token刷新功能完成
- [ ] Redis缓存集成
- [ ] 异常处理完善
- [ ] 事务管理正确

---

### Task 2.5: 认证Controller实现 ⏳

**前置条件**:
- ✅ Task 2.4 已完成

**文件**: `user-service/src/main/java/com/codeassistant/user/controller/AuthController.java`

**代码要求**:
```java
@RestController
@RequestMapping("/api/v1/auth")
@Tag(name = "认证接口", description = "用户注册、登录、Token管理")
public class AuthController {

    @Autowired
    private AuthService authService;

    /**
     * 用户注册
     */
    @PostMapping("/register")
    @Operation(summary = "用户注册", description = "创建新用户账号")
    public Result<UserResponse> register(@Valid @RequestBody RegisterRequest request) {
        UserResponse user = authService.register(request);
        return Result.success(user, "注册成功");
    }

    /**
     * 用户登录
     */
    @PostMapping("/login")
    @Operation(summary = "用户登录", description = "使用用户名或邮箱登录")
    public Result<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = authService.login(request);
        return Result.success(response, "登录成功");
    }

    /**
     * 刷新Token
     */
    @PostMapping("/refresh")
    @Operation(summary = "刷新Token", description = "使用Refresh Token获取新的Access Token")
    public Result<TokenResponse> refreshToken(@RequestBody Map<String, String> request) {
        String refreshToken = request.get("refreshToken");
        TokenResponse response = authService.refreshToken(refreshToken);
        return Result.success(response);
    }

    /**
     * 登出
     */
    @PostMapping("/logout")
    @Operation(summary = "登出", description = "清除用户会话")
    public Result<Void> logout(@RequestHeader("Authorization") String token) {
        // 从Redis中删除用户会话
        // 可选: 将Token加入黑名单
        return Result.success(null, "登出成功");
    }
}
```

**完成标准**:
- [ ] 所有接口实现完成
- [ ] Swagger注解完整
- [ ] 参数校验正确
- [ ] 返回格式统一

**验收测试**:
```bash
# 1. 测试注册
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test1234!"
  }'
# 预期: 返回用户信息，不包含密码

# 2. 测试登录
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "usernameOrEmail": "testuser",
    "password": "Test1234!"
  }'
# 预期: 返回accessToken和refreshToken

# 3. 测试受保护接口（无Token）
curl http://localhost:8080/api/v1/users/me
# 预期: 401 Unauthorized

# 4. 测试受保护接口（有Token）
TOKEN="<从登录获取的accessToken>"
curl http://localhost:8080/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
# 预期: 返回当前用户信息

# 5. 测试Token刷新
REFRESH_TOKEN="<从登录获取的refreshToken>"
curl -X POST http://localhost:8080/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refreshToken\": \"$REFRESH_TOKEN\"}"
# 预期: 返回新的accessToken
```

---

### Task 2.6: 用户管理接口 ⏳

**前置条件**:
- ✅ Task 2.5 已完成

**文件**: `user-service/src/main/java/com/codeassistant/user/controller/UserController.java`

**代码要求**:
```java
@RestController
@RequestMapping("/api/v1/users")
@Tag(name = "用户管理", description = "用户信息查询和更新")
public class UserController {

    @Autowired
    private UserService userService;

    /**
     * 获取当前登录用户信息
     */
    @GetMapping("/me")
    @Operation(summary = "获取当前用户", description = "获取当前登录用户的详细信息")
    public Result<UserResponse> getCurrentUser(@AuthenticationPrincipal UserDetails userDetails) {
        User user = userService.findByUsername(userDetails.getUsername());
        return Result.success(UserResponse.fromUser(user));
    }

    /**
     * 根据ID获取用户信息
     */
    @GetMapping("/{id}")
    @Operation(summary = "获取用户信息", description = "根据用户ID获取用户信息")
    public Result<UserResponse> getUserById(@PathVariable Long id) {
        User user = userService.findById(id);
        return Result.success(UserResponse.fromUser(user));
    }

    /**
     * 更新用户信息
     */
    @PutMapping("/me")
    @Operation(summary = "更新用户信息", description = "更新当前登录用户的信息")
    public Result<UserResponse> updateUser(
            @AuthenticationPrincipal UserDetails userDetails,
            @Valid @RequestBody UserUpdateRequest request) {
        User user = userService.updateUser(userDetails.getUsername(), request);
        return Result.success(UserResponse.fromUser(user));
    }

    /**
     * 修改密码
     */
    @PostMapping("/change-password")
    @Operation(summary = "修改密码", description = "修改当前用户密码")
    public Result<Void> changePassword(
            @AuthenticationPrincipal UserDetails userDetails,
            @Valid @RequestBody PasswordChangeRequest request) {
        userService.changePassword(userDetails.getUsername(), request);
        return Result.success(null, "密码修改成功");
    }
}
```

**完成标准**:
- [ ] 所有接口实现完成
- [ ] 需要认证的接口已保护
- [ ] 用户只能修改自己的信息

---

### Task 2.7: Phase 2 整体验收 ⏳

**验收清单**:

#### 1. 功能测试
```bash
# 完整用户流程测试
./scripts/test_user_flow.sh
```

**test_user_flow.sh内容**:
```bash
#!/bin/bash

BASE_URL="http://localhost:8080/api/v1"

echo "=== 1. 测试用户注册 ==="
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser_'$(date +%s)'",
    "email": "test'$(date +%s)'@example.com",
    "password": "Test1234!"
  }')
echo $REGISTER_RESPONSE | jq .

echo "=== 2. 测试用户登录 ==="
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "usernameOrEmail": "testuser",
    "password": "Test1234!"
  }')
echo $LOGIN_RESPONSE | jq .

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.accessToken')
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.refreshToken')

echo "=== 3. 测试获取当前用户信息 ==="
curl -s $BASE_URL/users/me \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "=== 4. 测试更新用户信息 ==="
curl -s -X PUT $BASE_URL/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "avatarUrl": "https://example.com/avatar.png"
  }' | jq .

echo "=== 5. 测试Token刷新 ==="
curl -s -X POST $BASE_URL/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refreshToken\": \"$REFRESH_TOKEN\"}" | jq .

echo "=== 6. 测试未授权访问 ==="
curl -s $BASE_URL/users/me
# 预期: 返回401

echo "=== 测试完成 ==="
```

#### 2. 单元测试
```bash
# 运行所有测试
cd java-service/user-service
mvn test

# 查看覆盖率
mvn jacoco:report
# 预期: 覆盖率 > 70%
```

#### 3. 文档更新检查
- [ ] CHANGELOG.md记录了所有认证功能
- [ ] PROJECTWIKI.md更新了API文档
- [ ] 数据库设计文档与实际一致
- [ ] Swagger文档完整

#### 4. 代码质量检查
- [ ] 所有Controller有Swagger注解
- [ ] 所有Service方法有JavaDoc
- [ ] 异常处理完善
- [ ] 日志记录合理

**Phase 2 完成标志**:
- ✅ 用户可以注册和登录
- ✅ JWT认证工作正常
- ✅ 受保护的接口需要Token
- ✅ Token可以刷新
- ✅ 单元测试覆盖率>70%
- ✅ 文档完整

**预估总时间**: Week 3-4 (15-20小时)

---

## Phase 3: 项目管理功能 (Week 5-6)

**目标**: 实现项目CRUD、GitHub仓库接入、Java调用Python服务。

**总体完成标准**:
- 用户可以创建项目
- 可以关联GitHub仓库
- Java可以调用Python服务进行代码索引
- 可以查询项目列表和详情

---

### Task 3.1: 项目实体和数据访问 ⏳

**前置条件**:
- ✅ Phase 2 已完成

**开发步骤**:

#### Step 1: Project实体类
**文件**: `project-service/src/main/java/com/codeassistant/project/entity/Project.java`

**代码要求**:
```java
@Data
@TableName("projects")
public class Project {
    @TableId(type = IdType.AUTO)
    private Long id;

    @TableField("user_id")
    private Long userId;

    @TableField("name")
    private String name;

    @TableField("description")
    private String description;

    @TableField("repository_url")
    private String repositoryUrl;

    @TableField("repository_type")
    private String repositoryType;  // GITHUB, GITLAB, LOCAL

    @TableField("status")
    private String status;  // CREATED, INDEXING, READY, ERROR

    @TableField("language")
    private String language;

    @TableField("total_files")
    private Integer totalFiles;

    @TableField("indexed_files")
    private Integer indexedFiles;

    @TableField("created_at")
    private LocalDateTime createdAt;

    @TableField("updated_at")
    private LocalDateTime updatedAt;

    @TableLogic
    @TableField("deleted")
    private Integer deleted;
}
```

**完成标准**:
- [ ] 实体类完成
- [ ] 数据库表创建
- [ ] Mapper接口完成

---

### Task 3.2: Agent客户端服务 ⏳

**前置条件**:
- ✅ Task 3.1 已完成
- ✅ Python Agent服务运行正常

**文件**: `project-service/src/main/java/com/codeassistant/project/service/AgentClientService.java`

**代码要求**:
```java
@Service
public class AgentClientService {

    @Value("${agent-service.url}")
    private String agentServiceUrl;

    private final RestTemplate restTemplate;

    /**
     * 调用Python服务索引代码仓库
     */
    public IndexResponse indexRepository(Long projectId, String repositoryUrl) {
        String url = agentServiceUrl + "/api/v1/index/repository";

        Map<String, Object> request = new HashMap<>();
        request.put("projectId", projectId);
        request.put("repositoryUrl", repositoryUrl);

        try {
            ResponseEntity<IndexResponse> response = restTemplate.postForEntity(
                url, request, IndexResponse.class);
            return response.getBody();
        } catch (Exception e) {
            log.error("Failed to call agent service", e);
            throw new BusinessException(ResultCode.AGENT_SERVICE_ERROR);
        }
    }

    /**
     * 查询索引状态
     */
    public IndexStatusResponse getIndexStatus(Long projectId) {
        String url = agentServiceUrl + "/api/v1/index/status/" + projectId;

        ResponseEntity<IndexStatusResponse> response =
            restTemplate.getForEntity(url, IndexStatusResponse.class);
        return response.getBody();
    }
}
```

**完成标准**:
- [ ] 可以调用Python服务
- [ ] 异常处理完善
- [ ] 超时配置合理

---

## Phase 4-6: 后续阶段

（文档太长，后续阶段简化描述）

### Phase 4: RAG问答Agent (Week 7-8)
- Python代码索引服务
- ChromaDB向量存储
- LangChain QA Chain
- 对话历史管理

### Phase 5: 代码审查Agent (Week 9-10)
- 静态代码分析
- LLM深度审查
- Celery异步任务
- 报告生成

### Phase 6: 性能优化与部署 (Week 11-12)
- Redis缓存优化
- Docker镜像构建
- docker-compose生产配置
- 文档完善

---

## 📊 进度追踪

### 当前状态
- **当前Phase**: Phase 1
- **当前Task**: Task 1.2
- **完成百分比**: 10%

### 下一步行动
1. 完成Task 1.2 - Java服务基础代码
2. 完成Task 1.3 - Python服务框架
3. 完成Task 1.4 - Docker-compose
4. Phase 1 整体验收

---

## 📝 使用说明

### 如何使用本文档

1. **按顺序开发**: 严格按照Phase和Task的顺序
2. **检查前置条件**: 开始新Task前确认前置条件满足
3. **完成标准验收**: 每个Task完成后进行验收测试
4. **更新进度**: 完成Task后更新本文档的进度
5. **同步其他文档**: 记得更新CHANGELOG和PROJECTWIKI

### Claude维护指引

当完成一个Task时:
1. 将该Task的状态改为 ✅
2. 更新"当前状态"章节
3. 在CHANGELOG.md添加变更记录
4. 如需要，更新PROJECTWIKI.md

---

**文档版本**: v1.0.0
**创建日期**: 2025-11-15
**最后更新**: 2025-11-15
