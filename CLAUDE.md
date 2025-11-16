# Claude 项目维护指南

本文档是给AI助手（Claude Code）的项目维护说明，确保项目文档的一致性和完整性。

---

## 📋 文档维护总则

### 核心原则

1. **及时性**: 每次代码变更都应该同步更新相关文档
2. **准确性**: 文档内容必须与实际代码保持一致
3. **完整性**: 重要变更必须在CHANGELOG中记录
4. **可追溯**: 所有决策和变更都要有清晰的记录

### 文档体系

```
code-assistant-platform/
├── README.md           # 项目概览（面向用户）
├── PROJECTWIKI.md      # 详细技术文档（面向开发者）
├── CHANGELOG.md        # 变更日志（版本追踪）
└── CLAUDE.md          # 本文档（维护指南）
```

---

## 📖 PROJECTWIKI.md 维护规范

### 何时更新

**必须更新的情况：**
- ✅ 添加新的服务或模块
- ✅ 修改架构设计
- ✅ 更新技术栈（版本升级、替换组件）
- ✅ 添加或修改API接口
- ✅ 修改数据库表结构
- ✅ 添加新的开发规范
- ✅ 解决了常见问题（添加到FAQ）
- ✅ 部署方式变更

**可选更新的情况：**
- ⚠️ 小的bug修复（不影响架构）
- ⚠️ 代码重构（不改变接口）
- ⚠️ 性能优化（重大优化需要记录）

### 更新内容对照表

| 代码变更类型 | 需要更新的WIKI章节 | 示例 |
|------------|------------------|------|
| 添加新服务 | 架构设计 + 模块说明 | 新增gateway-service |
| 新增API接口 | API接口文档 | POST /api/v1/users |
| 修改数据库 | 数据库设计 | 添加projects表 |
| 技术栈变更 | 技术栈详解 | MyBatis → MyBatis-Plus |
| 部署方式变更 | 部署指南 | 添加K8s部署 |
| 开发流程变更 | 开发指南 | 新增代码审查流程 |
| 常见问题 | 常见问题FAQ | 数据库连接失败解决方案 |

### 具体更新指南

#### 1. 架构设计章节

**更新时机**: 添加/删除服务、修改服务职责、改变通信方式

**更新步骤**:
```markdown
1. 更新架构图（ASCII图或说明）
2. 更新"服务职责划分"表格
3. 更新"服务间通信"说明
4. 如果影响技术选型，同步更新"技术栈详解"
```

**示例**:
```
变更: 添加了gateway-service

需要更新:
- 架构图中添加gateway层
- 服务职责划分表格添加gateway-service行
- 更新端口分配说明
- 通信流程图添加网关路由
```

#### 2. API接口文档章节

**更新时机**: 新增/修改/删除API接口

**格式要求**:
```markdown
**POST /api/v1/endpoint**
功能说明: [接口功能]

请求参数:
\`\`\`json
{
  "param1": "类型说明",
  "param2": "类型说明"
}
\`\`\`

响应示例:
\`\`\`json
{
  "code": 200,
  "data": { ... },
  "message": "success"
}
\`\`\`

错误码:
- 400: 参数错误
- 401: 未授权
- 404: 资源不存在
```

**更新清单**:
- [ ] 添加接口路径和HTTP方法
- [ ] 添加功能说明
- [ ] 添加请求参数示例（包含类型和必填说明）
- [ ] 添加响应示例（成功和失败）
- [ ] 添加认证要求（如果需要Token）
- [ ] 添加常见错误码

#### 3. 数据库设计章节

**更新时机**: 创建/修改数据库表、添加索引、修改字段

**格式要求**:
```markdown
### 表名 (table_name)
功能说明: [表的用途]

\`\`\`sql
CREATE TABLE table_name (
    id BIGSERIAL PRIMARY KEY,
    field_name VARCHAR(50) NOT NULL COMMENT '字段说明',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ...
);

-- 索引
CREATE INDEX idx_table_field ON table_name(field_name);
\`\`\`

字段说明:
- id: 主键，自增
- field_name: [字段用途和取值范围]
```

**更新清单**:
- [ ] 添加完整的CREATE TABLE语句
- [ ] 添加索引创建语句
- [ ] 添加字段说明（特别是枚举值）
- [ ] 标注外键关系
- [ ] 说明逻辑删除字段

#### 4. 常见问题FAQ章节

**何时添加**:
- 开发过程中遇到的坑
- 用户反馈的问题
- 部署时的常见错误
- 环境配置问题

**格式要求**:
```markdown
### Q[序号]: [问题简述]
**现象**: [详细描述问题现象]

**原因**: [问题根本原因]

**解决方案**:
\`\`\`bash
# 具体的解决步骤
step 1
step 2
\`\`\`

**预防措施**: [如何避免再次发生]
```

---

## 📝 CHANGELOG.md 维护规范

### 语义化版本规则

遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)

```
版本格式: 主版本号.次版本号.修订号 (MAJOR.MINOR.PATCH)

- MAJOR: 不兼容的API修改
- MINOR: 向下兼容的功能性新增
- PATCH: 向下兼容的问题修正
```

**示例**:
- 0.1.0 → 0.2.0: 添加了新功能（用户认证）
- 0.2.0 → 0.2.1: 修复了登录bug
- 0.2.1 → 1.0.0: 完成MVP，正式发布

### 何时更新

**每次代码变更后都要更新，具体规则：**

| 变更类型 | 更新章节 | 版本影响 |
|---------|---------|---------|
| 新增功能 | Added | MINOR +1 |
| 功能改进 | Changed | MINOR +1 |
| 废弃功能 | Deprecated | MINOR +1 |
| 移除功能 | Removed | MAJOR +1 |
| Bug修复 | Fixed | PATCH +1 |
| 安全修复 | Security | PATCH +1 |

### 更新流程

#### 开发阶段（版本号为 [未发布]）

**每次提交代码后**:
1. 在`## [未发布] - 开发中`章节下添加变更
2. 选择正确的分类（Added/Changed/Fixed等）
3. 使用复选框标记是否完成
4. 添加详细的变更说明

**格式示例**:
```markdown
## [未发布] - 开发中

### 新增 (Added)
- ✅ 用户注册接口 (user-service/controller/AuthController.java:25)
  - 支持邮箱和用户名注册
  - 密码BCrypt加密
  - 自动发送验证邮件
- ⏳ 项目创建接口 (开发中)

### 修复 (Fixed)
- ✅ 修复JWT过期时间计算错误 (JwtTokenProvider.java:67)
  - 问题: 过期时间单位错误导致Token立即失效
  - 影响: 所有需要认证的接口无法访问
  - 解决: 将毫秒转换为秒
```

**规范要点**:
- ✅ 使用复选框标记完成状态
- 📁 标注文件路径和行号（重要变更）
- 📊 说明影响范围
- 🔗 关联Issue或PR编号（如果有）

#### 版本发布时

**发布新版本的步骤**:
1. 将`[未发布]`章节改为`[版本号] - 日期`
2. 移除所有复选框
3. 整理和归类变更内容
4. 添加版本总结
5. 创建新的`[未发布]`章节

**格式示例**:
```markdown
## [0.2.0] - 2025-11-20

### 版本亮点
本版本实现了完整的用户认证系统，包括注册、登录、JWT认证和权限管理。

### 新增 (Added)
- 用户注册接口，支持邮箱验证
- 用户登录接口，返回JWT Token
- JWT认证过滤器，自动验证Token
- 用户信息查询接口
- Redis缓存用户会话

### 修复 (Fixed)
- JWT过期时间计算错误
- 密码加密算法配置问题

### 技术改进
- 引入Spring Security增强安全性
- 添加全局异常处理
- 完善API文档

### 测试
- 单元测试覆盖率达到75%
- 添加集成测试

### 文档
- 更新API接口文档
- 添加认证流程说明
- 完善开发指南

---

## [未发布] - 开发中

### 计划添加
- [ ] 项目管理功能
- [ ] GitHub仓库接入
```

### 变更分类详解

#### Added (新增)
**用于**: 新功能、新接口、新模块

**示例**:
```markdown
### 新增 (Added)
- ✅ 用户认证系统
  - JWT Token生成和验证
  - 密码BCrypt加密
  - Redis会话管理
- ✅ Swagger API文档
  - 自动生成接口文档
  - 在线测试功能
```

#### Changed (变更)
**用于**: 功能改进、接口修改、配置更新

**示例**:
```markdown
### 变更 (Changed)
- ✅ 优化数据库连接池配置
  - 最大连接数: 20 → 50
  - 超时时间: 30s → 10s
  - 提升并发性能30%
- ✅ 修改用户登录响应格式
  - 添加用户角色信息
  - 添加Token过期时间
```

#### Deprecated (废弃)
**用于**: 标记即将移除的功能

**示例**:
```markdown
### 废弃 (Deprecated)
- ⚠️ /api/v1/auth/old-login 接口已废弃
  - 将在v0.3.0版本移除
  - 请使用 /api/v1/auth/login 替代
```

#### Removed (移除)
**用于**: 删除的功能、接口、依赖

**示例**:
```markdown
### 移除 (Removed)
- ❌ 移除旧版认证接口
- ❌ 移除未使用的依赖: commons-lang 2.x
```

#### Fixed (修复)
**用于**: Bug修复

**示例**:
```markdown
### 修复 (Fixed)
- ✅ 修复用户注册时邮箱重复检查失败的问题
  - Issue: #123
  - 影响: 允许重复邮箱注册
  - 根因: SQL查询条件错误
  - 解决: 修正WHERE子句
- ✅ 修复Redis连接超时问题
  - 调整连接池配置
  - 添加重试机制
```

#### Security (安全)
**用于**: 安全漏洞修复

**示例**:
```markdown
### 安全 (Security)
- 🔒 修复SQL注入漏洞
  - 位置: UserController查询接口
  - 风险等级: 高
  - 解决: 使用参数化查询
- 🔒 更新依赖版本修复CVE-2024-XXXX
```

---

## 🔄 文档更新工作流

### 标准流程

```
代码变更
    ↓
┌─────────────────┐
│ 1. 提交代码      │
└─────────────────┘
    ↓
┌─────────────────┐
│ 2. 更新CHANGELOG │ ← 记录本次变更
│   - 选择分类     │
│   - 添加描述     │
│   - 标记状态     │
└─────────────────┘
    ↓
┌─────────────────┐
│ 3. 检查是否需要  │
│    更新WIKI      │
└─────────────────┘
    ↓
    ├→ 架构/API变更 → 更新PROJECTWIKI.md对应章节
    ├→ 数据库变更   → 更新数据库设计章节
    ├→ 配置变更     → 更新开发/部署指南
    └→ 小改动       → 无需更新WIKI
```

### 检查清单

**每次代码提交前检查**:
- [ ] CHANGELOG.md已更新（添加变更记录）
- [ ] 如果修改了API，PROJECTWIKI.md的API章节已更新
- [ ] 如果修改了数据库，数据库设计章节已更新
- [ ] 如果添加了新模块，模块说明章节已更新
- [ ] 如果解决了常见问题，FAQ章节已更新

**版本发布前检查**:
- [ ] CHANGELOG.md整理完毕（分类清晰、描述完整）
- [ ] 版本号已更新（遵循语义化版本）
- [ ] 添加版本亮点总结
- [ ] PROJECTWIKI.md与实际代码一致
- [ ] README.md的路线图已更新

---

## 🎨 前端开发规范

### 设计风格

本项目前端采用 **Neo-Brutalism（新粗野主义）+ 硬阴影贴纸感** 设计风格。

**核心特征：**
- 黑色实线边框（1-3px）
- 无模糊、位移型硬阴影
- 黑白为底 + 1-2个点缀纯色
- 直角或极小圆角（2px）
- 高对比度，拒绝柔和

**技术栈：**
- React 18 + TypeScript
- Tailwind CSS
- Vite
- Zustand（状态管理）

**详细规范：** 请参考 `docs/FRONTEND_DESIGN_SPEC.md`

### 前端开发时必须遵循

当开发前端代码时，**必须**：
1. 阅读并遵循 `docs/FRONTEND_DESIGN_SPEC.md` 的所有规范
2. 使用定义的 Design Tokens
3. 复用封装的基础组件（BrutButton, BrutCard等）
4. 遵循可访问性要求（AA对比度、键盘可用、可见焦点）
5. 检查 Do/Don't 清单

**风格禁令（绝对禁止）：**
- ❌ 玻璃拟态 (Glassmorphism)
- ❌ 渐变背景
- ❌ 柔和/模糊阴影
- ❌ 大圆角
- ❌ 半透明效果

---

## 📐 格式规范

### Markdown格式

**标题层级**:
```markdown
# 一级标题 - 文档标题
## 二级标题 - 主要章节
### 三级标题 - 子章节
#### 四级标题 - 详细说明
```

**列表**:
```markdown
有序列表:
1. 第一项
2. 第二项

无序列表:
- 项目1
- 项目2

任务列表:
- [x] 已完成
- [ ] 未完成
```

**代码块**:
````markdown
```语言
代码内容
```

示例:
```java
public class User {
    private Long id;
}
```
````

**表格**:
```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 内容1 | 内容2 | 内容3 |
```

### 图标使用规范

**状态标识**:
- ✅ 已完成
- ⏳ 进行中
- ❌ 已移除
- ⚠️ 警告/废弃
- 🔒 安全相关
- 🚀 性能优化
- 📝 文档
- 🐛 Bug修复
- 🎨 UI/样式
- ♻️ 重构

**模块标识**:
- 🎯 核心功能
- 🤖 Agent相关
- 🔐 认证/权限
- 💾 数据库
- 🔧 配置/工具
- 📊 监控/日志

---

## 🎯 实际操作示例

### 场景1: 添加了用户注册接口

**代码变更**:
```java
// AuthController.java
@PostMapping("/register")
public Result register(@RequestBody RegisterRequest request) {
    // 实现代码...
}
```

**需要更新的文档**:

1. **CHANGELOG.md**:
```markdown
## [未发布] - 开发中

### 新增 (Added)
- ✅ 用户注册接口 (user-service/controller/AuthController.java:25)
  - 支持用户名、邮箱、密码注册
  - 自动进行邮箱格式验证
  - 密码强度校验（最少8位，包含数字和字母）
  - 密码BCrypt加密存储
  - 自动创建用户默认角色
```

2. **PROJECTWIKI.md** (API接口文档章节):
```markdown
#### 认证接口

**POST /api/v1/auth/register**
用户注册接口

请求参数:
\`\`\`json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Password123!"
}
\`\`\`

参数说明:
- username: 用户名，3-20个字符，只能包含字母、数字、下划线
- email: 邮箱地址，必须是有效格式
- password: 密码，8-20个字符，必须包含数字和字母

响应示例:
\`\`\`json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "userId": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
\`\`\`

错误码:
- 400: 参数验证失败（用户名/邮箱格式错误、密码强度不够）
- 409: 用户名或邮箱已存在
```

---

### 场景2: 修复了JWT过期时间bug

**代码变更**:
```java
// JwtTokenProvider.java
// 修复前
long expirationTime = System.currentTimeMillis() + jwtExpiration;

// 修复后
long expirationTime = System.currentTimeMillis() + jwtExpiration * 1000;
```

**需要更新的文档**:

**CHANGELOG.md**:
```markdown
## [未发布] - 开发中

### 修复 (Fixed)
- ✅ 修复JWT Token过期时间计算错误 (JwtTokenProvider.java:67)
  - Issue: Token立即失效，用户无法保持登录状态
  - 根因: 配置的过期时间单位为秒，但代码直接使用导致过期时间错误
  - 影响: 所有需要认证的接口返回401
  - 解决: 将配置值乘以1000转换为毫秒
  - 测试: 验证Token在配置的时间后正常过期
```

**PROJECTWIKI.md**: 无需更新（Bug修复未改变接口行为）

---

### 场景3: 添加了projects表

**代码变更**:
```sql
CREATE TABLE projects (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    ...
);
```

**需要更新的文档**:

1. **CHANGELOG.md**:
```markdown
## [未发布] - 开发中

### 新增 (Added)
- ✅ 项目管理数据库表设计
  - projects表: 存储项目基本信息
  - 支持关联用户、仓库URL、索引状态等
  - 添加必要的索引优化查询性能
```

2. **PROJECTWIKI.md** (数据库设计章节):
```markdown
### 项目表 (projects)
存储用户创建的代码项目信息

\`\`\`sql
CREATE TABLE projects (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    repository_url VARCHAR(255),
    repository_type VARCHAR(20),  -- GITHUB, GITLAB, LOCAL
    status VARCHAR(20) DEFAULT 'CREATED',
    ...
);

CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
\`\`\`

字段说明:
- id: 主键
- user_id: 所属用户ID，外键关联users表
- name: 项目名称
- repository_type: 仓库类型（GITHUB/GITLAB/LOCAL）
- status: 项目状态
  - CREATED: 已创建
  - INDEXING: 索引中
  - READY: 就绪
  - ERROR: 错误
```

---

## ⚠️ 常见错误和注意事项

### 容易忘记更新的情况

1. **修改了配置文件但未更新文档**
   - application.yml端口变更 → 更新WIKI部署指南
   - 环境变量新增 → 更新.env.example和WIKI

2. **API响应格式变更**
   - 添加/删除字段 → 更新API文档示例
   - 错误码变更 → 更新错误码说明

3. **数据库字段枚举值变更**
   - 添加新的status值 → 更新字段说明

### 文档冲突解决

如果PROJECTWIKI.md过大难以维护:
1. 考虑拆分为多个文档（放在docs/目录）
2. PROJECTWIKI.md作为索引，链接到具体文档
3. 保持每个文档单一职责

### 版本号管理

**开发阶段**:
- 所有变更都记录在`[未发布]`章节
- 不要提前分配版本号

**发布时**:
- 根据变更类型确定版本号
- 如果同时有MAJOR和MINOR变更，按MAJOR处理
- 每次发布必须更新版本号

---

## ✅ 文档质量检查清单

### 提交前自检

**CHANGELOG.md**:
- [ ] 变更记录已添加到正确的分类
- [ ] 描述清晰，包含必要的上下文
- [ ] 重要变更标注了文件路径
- [ ] 使用了正确的图标和标记
- [ ] 日期格式正确（YYYY-MM-DD）

**PROJECTWIKI.md**:
- [ ] 新增的API有完整的请求/响应示例
- [ ] 新增的表有完整的CREATE语句和字段说明
- [ ] 架构图与实际代码一致
- [ ] 代码示例可以运行（或标注伪代码）
- [ ] 链接有效（内部锚点、外部链接）

**通用**:
- [ ] Markdown格式正确（无语法错误）
- [ ] 中英文之间有空格（排版规范）
- [ ] 代码块指定了语言类型
- [ ] 表格对齐美观
- [ ] 没有拼写错误

---

## 🤖 给Claude的特别提示

### 主动更新原则

当用户进行以下操作时，**主动建议**更新文档:
- 创建新文件/模块
- 修改API接口
- 更改数据库结构
- 解决重要bug
- 完成一个功能模块

### 更新建议模板

```markdown
✅ 代码已更新完成！

📝 建议同步更新文档:

**CHANGELOG.md**:
- 在 [未发布] > [新增] 章节添加:
  "用户注册接口实现，支持邮箱验证和密码加密"

**PROJECTWIKI.md**:
- 在 API接口文档 章节添加注册接口的详细说明
- 包含请求参数、响应示例、错误码

是否需要我帮你更新这些文档？
```

### 版本发布时的提醒

当用户完成一个阶段性功能时，提醒:
```markdown
🎉 功能开发完成！

建议发布新版本:
- 当前未发布的变更包含: [列出主要变更]
- 建议版本号: v0.2.0 (添加了用户认证功能)
- 需要整理CHANGELOG并创建版本标记

是否需要我帮你整理版本文档？
```

---

## 📚 参考资料

- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)
- [语义化版本](https://semver.org/lang/zh-CN/)
- [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)
- [中文文案排版指北](https://github.com/sparanoid/chinese-copywriting-guidelines)

---

**文档版本**: v1.0.0
**最后更新**: 2025-11-15
**维护者**: Claude Code AI Assistant
