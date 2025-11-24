# Code Assistant Platform - Web Client

基于 **Neo-Brutalism (新粗野主义)** 设计风格的前端应用。

## 🎨 设计风格

### 核心特征
- ✅ **黑色实线边框** (2-3px)
- ✅ **无模糊硬阴影** (offset型)
- ✅ **黑白为底** + 1-2个点缀纯色
- ✅ **直角或极小圆角** (2px)
- ✅ **高对比度**

### 禁用风格
- ❌ 玻璃拟态 (Glassmorphism)
- ❌ 渐变背景
- ❌ 柔和/模糊阴影
- ❌ 大圆角
- ❌ 半透明效果

## 🛠️ 技术栈

- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Zustand** - 状态管理
- **React Router** - 路由管理
- **Axios** - HTTP客户端

## 📦 项目结构

```
web-client/
├── src/
│   ├── components/         # Neo-Brutalism 基础组件
│   │   ├── BrutButton.tsx  # 按钮组件
│   │   ├── BrutCard.tsx    # 卡片组件
│   │   ├── BrutInput.tsx   # 输入框组件
│   │   └── BrutContainer.tsx # 容器组件
│   ├── pages/              # 页面组件
│   │   ├── LoginPage.tsx   # 登录页面
│   │   ├── RegisterPage.tsx # 注册页面
│   │   └── HomePage.tsx    # 主页
│   ├── stores/             # 状态管理
│   │   ├── authStore.ts    # 认证状态
│   │   └── projectStore.ts # 项目状态
│   ├── services/           # API服务
│   │   └── api.ts          # API配置和接口
│   ├── App.tsx             # 应用根组件
│   ├── main.tsx            # 应用入口
│   └── index.css           # 全局样式
├── .env                    # 环境变量
└── tailwind.config.js      # Tailwind配置
```

## 🚀 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:5173

### 构建生产版本

```bash
npm run build
```

## 🎯 已实现功能

### ✅ 基础设施
- [x] React + Vite + TypeScript 项目配置
- [x] Tailwind CSS + Neo-Brutalism Design Tokens
- [x] 路由配置 (React Router)
- [x] 状态管理 (Zustand)
- [x] API 服务封装

### ✅ 基础组件
- [x] BrutButton - 硬边框按钮 (default/primary/danger/secondary)
- [x] BrutCard - 硬阴影卡片 (default/yellow/blue)
- [x] BrutInput - 聚焦动画输入框
- [x] BrutContainer - 响应式容器

### ✅ 页面功能
- [x] 登录页面 (LoginPage)
  - 用户名/密码登录
  - 表单验证
  - 错误提示
- [x] 注册页面 (RegisterPage)
  - 用户注册
  - 密码确认
  - 邮箱验证
- [x] 主页 (HomePage)
  - 项目列表展示
  - 用户信息显示
  - 退出登录
  - 受保护路由

### ✅ 状态管理
- [x] 认证状态 (authStore)
  - 登录/登出
  - Token管理
  - 自动初始化
- [x] 项目状态 (projectStore)
  - 项目列表
  - CRUD操作

### ✅ API集成
- [x] 认证API (user-service)
  - POST /api/v1/auth/login
  - POST /api/v1/auth/register
  - GET /api/v1/auth/me
- [x] 项目API (user-service)
  - GET /api/v1/projects
  - POST /api/v1/projects
  - PUT /api/v1/projects/:id
  - DELETE /api/v1/projects/:id
- [x] Agent API (agent-service)
  - POST /api/v1/chat

## ⏭️ 待开发功能

### 🔲 项目管理页面
- [ ] 创建项目模态框
- [ ] 项目详情页
- [ ] 项目设置
- [ ] 仓库连接

### 🔲 AI 对话页面
- [ ] 聊天界面
- [ ] 代码高亮显示
- [ ] 流式响应
- [ ] 历史记录

### 🔲 增强功能
- [ ] 响应式布局优化
- [ ] 加载状态优化
- [ ] 错误边界
- [ ] Toast通知
- [ ] 键盘快捷键

## 🎨 设计规范

详细设计规范请参考: `../docs/FRONTEND_DESIGN_SPEC.md`

## 🔧 环境变量

```env
VITE_API_BASE_URL=http://localhost:8080      # Java后端服务
VITE_AGENT_API_BASE_URL=http://localhost:8000 # Python AI服务
```

## 📝 开发注意事项

1. **严格遵循 Neo-Brutalism 设计风格**
   - 使用预定义的组件和样式类
   - 不要引入柔和阴影或渐变

2. **组件复用**
   - 优先使用 `components/` 目录下的基础组件
   - 保持组件的单一职责

3. **状态管理**
   - 全局状态使用 Zustand stores
   - 组件内部状态使用 useState

4. **API调用**
   - 使用 `services/api.ts` 中封装的方法
   - 统一的错误处理和Token管理

## 🌐 后端服务依赖

- **User Service**: http://localhost:8080
  - 用户认证
  - 项目管理

- **Agent Service**: http://localhost:8000
  - AI对话
  - 代码分析

---

**版本**: v0.1.0 (开发中)
**最后更新**: 2025-11-16
