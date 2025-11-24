import axios from 'axios';

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器 - 添加token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期,清除本地存储并跳转到登录页
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证相关API
export const authAPI = {
  login: (credential: string, password: string) =>
    api.post('/api/v1/auth/login', { credential, password }),

  register: (username: string, email: string, password: string) =>
    api.post('/api/v1/auth/register', { username, email, password }),

  getCurrentUser: () =>
    api.get('/api/v1/auth/me')
};

// 项目相关API
export const projectAPI = {
  getProjects: () =>
    api.get('/api/v1/projects'),

  getProjectById: (id: number) =>
    api.get(`/api/v1/projects/${id}`),

  createProject: (data: {
    name: string;
    description?: string;
    repositoryUrl?: string;
    repositoryType?: string;
    localPath?: string;
  }) =>
    api.post('/api/v1/projects', data),

  updateProject: (id: number, data: any) =>
    api.put(`/api/v1/projects/${id}`, data),

  deleteProject: (id: number) =>
    api.delete(`/api/v1/projects/${id}`)
};

// AI Agent相关API (连接Python服务)
const AGENT_API_BASE_URL = import.meta.env.VITE_AGENT_API_BASE_URL || 'http://localhost:8000';

// 保留旧的快速问答接口（直接走 Python Agent，不落库）
export const agentAPI = {
  chat: (projectId: number, message: string) =>
    axios.post(`${AGENT_API_BASE_URL}/api/v1/chat`, {
      project_id: projectId,
      message
    })
};

// 对话与历史管理 API（走 Java user-service，对话/消息持久化）
export const chatAPI = {
  // 创建对话
  createConversation: (projectId: number, title?: string) =>
    api.post('/api/v1/chat/conversations', {
      projectId,
      title: title || '新对话'
    }),

  // 获取项目的对话列表
  getConversations: (projectId: number) =>
    api.get(`/api/v1/chat/conversations/${projectId}`),

  // 发送消息（带历史记录）
  sendMessage: (conversationId: string, content: string) =>
    api.post(`/api/v1/chat/${conversationId}/messages`, { content }),

  // 获取消息历史（全部）
  getMessages: (conversationId: string) =>
    api.get(`/api/v1/chat/${conversationId}/messages`),

  // 分页获取消息
  getMessagesPaged: (conversationId: string, pageNum: number, pageSize: number) =>
    api.get(`/api/v1/chat/${conversationId}/messages/paged`, {
      params: { pageNum, pageSize }
    })
};

// Code Review 相关API (通过Java后端调用)
export const reviewAPI = {
  // 触发代码审查
  startReview: (projectId: number, level: 'quick' | 'standard' | 'full' = 'standard') =>
    api.post(`/api/v1/projects/${projectId}/review`, { level }),

  // 获取审查结果
  getReviewResult: (projectId: number, taskId: string) =>
    api.get(`/api/v1/projects/${projectId}/review/${taskId}`)
};

// WebSocket 配置
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'http://localhost:8080/ws';
