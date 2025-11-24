import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BrutButton, BrutCard, BrutContainer, ReviewReport } from '../components';
import { projectAPI, reviewAPI, chatAPI } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { useTaskProgress, type ReviewReport as ReviewReportType } from '../hooks/useTaskProgress';

interface Project {
  id: number;
  userId: number;
  name: string;
  description: string | null;
  repositoryUrl: string | null;
  repositoryType: string;
  status: string;
  indexStatus: string;
  language: string | null;
  totalFiles: number;
  indexedFiles: number;
  lastIndexedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

/**
 * 项目详情页面
 * 遵循 Neo-Brutalism 设计风格
 */
export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // 审查相关状态
  const [reviewTaskId, setReviewTaskId] = useState<string | null>(null);
  const [reviewReport, setReviewReport] = useState<ReviewReportType | null>(null);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewError, setReviewError] = useState('');

  // 对话与聊天状态
  const [conversations, setConversations] = useState<Array<{
    id: string;
    title: string;
    createdAt: string;
  }> | null>(null);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  type ChatMessage = {
    id: number;
    role: 'user' | 'assistant';
    content: string;
    createdAt: string;
    sources?: {
      filePath: string;
      startLine: number;
      endLine: number;
    }[] | null;
  };

  const [messages, setMessages] = useState<ChatMessage[] | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // WebSocket 订阅任务进度
  const handleReviewComplete = useCallback((report: ReviewReportType) => {
    setReviewReport(report);
    setReviewTaskId(null);
    setReviewLoading(false);
  }, []);

  const handleReviewError = useCallback((err: string) => {
    setReviewError(err);
    setReviewTaskId(null);
    setReviewLoading(false);
  }, []);

  const { progress, connected } = useTaskProgress(reviewTaskId, {
    onComplete: handleReviewComplete,
    onError: handleReviewError
  });

  useEffect(() => {
    if (projectId) {
      loadProject(parseInt(projectId, 10));
    }
  }, [projectId]);

  const loadProject = async (id: number) => {
    try {
      const response = await projectAPI.getProjectById(id);
      if (response.data.code === 200) {
        setProject(response.data.data);
      } else {
        setError(response.data.message || '加载项目失败');
      }
    } catch (err: any) {
      console.error('Failed to load project:', err);
      setError(err.response?.data?.message || '加载项目失败');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // 加载项目下的对话列表
  const loadConversations = async (projectId: number) => {
    try {
      const res = await chatAPI.getConversations(projectId);
      if (res.data.code === 200) {
        setConversations(res.data.data || []);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  // 加载指定对话的消息历史
  const loadMessages = async (conversationId: string) => {
    try {
      const res = await chatAPI.getMessages(conversationId);
      if (res.data.code === 200) {
        setMessages(res.data.data || []);
      }
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const handleOpenChat = async () => {
    if (!project) return;
    setChatError('');

    // 首次点击时加载对话列表
    if (!conversations) {
      await loadConversations(project.id);
    }
  };

  const handleSelectConversation = async (conversationId: string) => {
    setSelectedConversationId(conversationId);
    await loadMessages(conversationId);
  };

  const handleCreateConversation = async () => {
    if (!project) return;
    setChatError('');
    try {
      const res = await chatAPI.createConversation(project.id, `对话 ${new Date().toLocaleString('zh-CN')}`);
      if (res.data.code === 200 && res.data.data) {
        const conv = res.data.data;
        const next = [...(conversations || []), conv];
        setConversations(next);
        setSelectedConversationId(conv.id);
        setMessages([]);
      } else {
        setChatError(res.data.message || '创建对话失败');
      }
    } catch (err: any) {
      console.error('Create conversation error:', err);
      setChatError(err.response?.data?.message || '创建对话失败');
    }
  };

  const handleSendMessage = async () => {
    if (!selectedConversationId || !chatInput.trim()) return;
    setChatLoading(true);
    setChatError('');
    try {
      const res = await chatAPI.sendMessage(selectedConversationId, chatInput.trim());
      if (res.data.code === 200 && res.data.data) {
        // 发送成功后，简单重新加载消息列表，确保包含模型回复
        await loadMessages(selectedConversationId);
        setChatInput('');
      } else {
        setChatError(res.data.message || '发送消息失败');
      }
    } catch (err: any) {
      console.error('Send message error:', err);
      setChatError(err.response?.data?.message || '发送消息失败');
    } finally {
      setChatLoading(false);
    }
  };

  // 消息更新后自动滚动到底部
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [messages]);

  // 触发代码审查
  const handleStartReview = async (level: 'quick' | 'standard' | 'full' = 'standard') => {
    if (!project) return;

    setReviewLoading(true);
    setReviewError('');
    setReviewReport(null);

    try {
      const response = await reviewAPI.startReview(project.id, level);
      if (response.data.code === 200) {
        setReviewTaskId(response.data.data.taskId);
      } else {
        setReviewError(response.data.message || '启动审查失败');
        setReviewLoading(false);
      }
    } catch (err: any) {
      console.error('Failed to start review:', err);
      setReviewError(err.response?.data?.message || '启动审查失败');
      setReviewLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'CREATED':
        return 'bg-brut-gray-300';
      case 'INDEXING':
        return 'bg-brut-yellow';
      case 'READY':
        return 'bg-brut-green';
      case 'ERROR':
        return 'bg-brut-red';
      default:
        return 'bg-brut-gray-300';
    }
  };

  const getIndexStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING':
        return 'bg-brut-gray-300';
      case 'INDEXING':
        return 'bg-brut-yellow';
      case 'COMPLETED':
        return 'bg-brut-green';
      case 'FAILED':
        return 'bg-brut-red';
      default:
        return 'bg-brut-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-brut-gray-100 flex items-center justify-center">
        <p className="text-xl font-bold">加载中...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-brut-gray-100">
        <BrutContainer>
          <div className="py-12 text-center">
            <BrutCard className="max-w-md mx-auto">
              <h2 className="brut-h3 mb-4 text-brut-red">加载失败</h2>
              <p className="mb-6">{error || '项目不存在'}</p>
              <BrutButton variant="secondary" onClick={() => navigate('/')}>
                返回首页
              </BrutButton>
            </BrutCard>
          </div>
        </BrutContainer>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-brut-gray-100">
      {/* 顶部导航栏 */}
      <header className="bg-brut-yellow border-b-brut border-brut-black shadow-brut-md">
        <BrutContainer>
          <div className="h-16 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <BrutButton
                variant="secondary"
                size="sm"
                onClick={() => navigate('/')}
              >
                ← 返回
              </BrutButton>
              <h1 className="brut-h3">CODE ASSISTANT</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="font-bold">你好, {user?.username}</span>
              <BrutButton variant="secondary" size="sm" onClick={handleLogout}>
                退出登录
              </BrutButton>
            </div>
          </div>
        </BrutContainer>
      </header>

      {/* 主内容区 */}
      <main className="py-8">
        <BrutContainer>
          {/* 项目标题和状态 */}
          <div className="mb-8">
            <div className="flex justify-between items-start mb-4">
              <h2 className="brut-h2">{project.name}</h2>
              <div className="flex gap-2">
                <span
                  className={`px-3 py-1 text-xs font-bold border-brut border-brut-black ${getStatusColor(project.status)}`}
                >
                  {project.status}
                </span>
                <span
                  className={`px-3 py-1 text-xs font-bold border-brut border-brut-black ${getIndexStatusColor(project.indexStatus)}`}
                >
                  索引: {project.indexStatus}
                </span>
              </div>
            </div>
            {project.description && (
              <p className="text-lg">{project.description}</p>
            )}
          </div>

          {/* 项目信息卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <BrutCard variant="default">
              <h3 className="brut-h4 mb-4">基本信息</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-bold text-brut-gray-600">
                    项目ID
                  </label>
                  <p className="font-mono">{project.id}</p>
                </div>
                <div>
                  <label className="block text-sm font-bold text-brut-gray-600">
                    仓库类型
                  </label>
                  <p>{project.repositoryType}</p>
                </div>
                {project.repositoryUrl && (
                  <div>
                    <label className="block text-sm font-bold text-brut-gray-600">
                      仓库地址
                    </label>
                    <a
                      href={project.repositoryUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brut-blue hover:underline break-all"
                    >
                      {project.repositoryUrl}
                    </a>
                  </div>
                )}
                {project.language && (
                  <div>
                    <label className="block text-sm font-bold text-brut-gray-600">
                      主要语言
                    </label>
                    <p>{project.language}</p>
                  </div>
                )}
              </div>
            </BrutCard>

            <BrutCard variant="default">
              <h3 className="brut-h4 mb-4">索引统计</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-bold text-brut-gray-600">
                    总文件数
                  </label>
                  <p className="text-2xl font-bold">{project.totalFiles}</p>
                </div>
                <div>
                  <label className="block text-sm font-bold text-brut-gray-600">
                    已索引文件数
                  </label>
                  <p className="text-2xl font-bold">{project.indexedFiles}</p>
                </div>
                {project.lastIndexedAt && (
                  <div>
                    <label className="block text-sm font-bold text-brut-gray-600">
                      最后索引时间
                    </label>
                    <p>{formatDate(project.lastIndexedAt)}</p>
                  </div>
                )}
              </div>
            </BrutCard>
          </div>

          {/* 时间信息 */}
          <BrutCard variant="default" className="mb-8">
            <h3 className="brut-h4 mb-4">时间信息</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-bold text-brut-gray-600">
                  创建时间
                </label>
                <p>{formatDate(project.createdAt)}</p>
              </div>
              <div>
                <label className="block text-sm font-bold text-brut-gray-600">
                  最后更新
                </label>
                <p>{formatDate(project.updatedAt)}</p>
              </div>
            </div>
          </BrutCard>

          {/* 代码审查区域 */}
          <BrutCard variant="default" className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="brut-h4">代码审查</h3>
              {connected && (
                <span className="text-xs text-green-600 font-bold">
                  WebSocket 已连接
                </span>
              )}
            </div>

            {/* 审查按钮 */}
            <div className="flex gap-3 mb-4">
              <BrutButton
                variant="primary"
                onClick={() => handleStartReview('standard')}
                disabled={reviewLoading || project.indexStatus !== 'COMPLETED'}
              >
                {reviewLoading ? '审查中...' : '开始代码审查'}
              </BrutButton>
              <BrutButton
                variant="secondary"
                onClick={() => handleStartReview('quick')}
                disabled={reviewLoading || project.indexStatus !== 'COMPLETED'}
              >
                快速审查
              </BrutButton>
              <BrutButton
                variant="secondary"
                onClick={() => handleStartReview('full')}
                disabled={reviewLoading || project.indexStatus !== 'COMPLETED'}
              >
                完整审查
              </BrutButton>
            </div>

            {project.indexStatus !== 'COMPLETED' && (
              <p className="text-sm text-gray-500">
                请先完成代码索引后再进行审查
              </p>
            )}

            {/* 审查进度条 */}
            {reviewLoading && progress && (
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-2">
                  <span>{progress.message || '处理中...'}</span>
                  <span>{progress.progress}%</span>
                </div>
                <div className="w-full h-4 bg-gray-200 border-2 border-black">
                  <div
                    className="h-full bg-brut-yellow transition-all duration-300"
                    style={{ width: `${progress.progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* 审查完成状态提示（保留 100% 信息） */}
            {!reviewLoading && progress && progress.status === 'COMPLETED' && (
              <div className="mt-4 text-sm font-bold text-green-700">
                审查已完成（{progress.progress}%）
              </div>
            )}

            {/* 审查错误 */}
            {reviewError && (
              <div className="mt-4 p-3 bg-red-100 border-2 border-red-500 text-red-700">
                {reviewError}
              </div>
            )}
          </BrutCard>

          {/* 审查报告 */}
          {reviewReport && (
            <div className="mb-8">
              <h3 className="brut-h4 mb-4">审查报告</h3>
              <ReviewReport report={reviewReport} />
            </div>
          )}

          {/* 对话与历史（基础版） */}
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 对话列表 */}
            <BrutCard className="lg:col-span-1">
              <div className="flex items-center justify-between mb-4">
                <h3 className="brut-h4">对话列表</h3>
                <BrutButton size="sm" variant="secondary" onClick={handleCreateConversation}>
                  新建对话
                </BrutButton>
              </div>
              <BrutButton
                variant="primary"
                className="w-full mb-3"
                onClick={() => {
                  if (project) loadConversations(project.id);
                }}
              >
                刷新对话
              </BrutButton>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {conversations && conversations.length > 0 ? (
                  conversations.map((c) => (
                    <button
                      key={c.id}
                      className={`w-full text-left px-3 py-2 border-2 border-black ${
                        selectedConversationId === c.id ? 'bg-brut-yellow' : 'bg-white'
                      }`}
                      onClick={() => handleSelectConversation(c.id)}
                    >
                      <div className="font-bold text-sm line-clamp-1">{c.title}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(c.createdAt).toLocaleString('zh-CN')}
                      </div>
                    </button>
                  ))
                ) : (
                  <p className="text-sm text-gray-500">暂无对话，点击“新建对话”开始一轮新对话。</p>
                )}
              </div>
            </BrutCard>

            {/* 消息历史 + 输入框 */}
            <BrutCard className="lg:col-span-2">
              <div className="flex items-center justify-between mb-4">
                <h3 className="brut-h4">对话历史</h3>
                <BrutButton size="sm" variant="secondary" onClick={handleOpenChat}>
                  查看历史
                </BrutButton>
              </div>
              {chatError && (
                <div className="mb-3 p-2 bg-red-100 border-2 border-red-500 text-sm text-red-700">
                  {chatError}
                </div>
              )}
              <div
                ref={messagesEndRef}
                className="h-64 border-2 border-black bg-white overflow-y-auto mb-4 p-3 space-y-3"
              >
                {selectedConversationId && messages && messages.length > 0 ? (
                  messages.map((m) => (
                    <div key={m.id} className="border-b border-dashed border-gray-300 pb-2">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>{m.role === 'user' ? '你' : '助手'}</span>
                        <span>{new Date(m.createdAt).toLocaleString('zh-CN')}</span>
                      </div>
                      <div className="text-sm whitespace-pre-wrap">{m.content}</div>
                      {m.role === 'assistant' && m.sources && m.sources.length > 0 && (
                        <div className="mt-1 text-xs text-gray-500">
                          <div className="font-bold">引用代码:</div>
                          <ul className="list-disc list-inside">
                            {m.sources.map((s, index) => (
                              <li key={index}>
                                {s.filePath} [{s.startLine}-{s.endLine}]
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-500">
                    请选择左侧的对话查看历史，或创建一个新对话。
                  </p>
                )}
              </div>
              <div className="flex gap-3">
                <input
                  className="flex-1 px-3 py-2 border-2 border-black bg-white font-mono text-sm focus:outline-none focus:ring-0"
                  placeholder="输入消息，回车发送"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  disabled={!selectedConversationId || chatLoading}
                />
                <BrutButton
                  variant="primary"
                  onClick={handleSendMessage}
                  disabled={!selectedConversationId || chatLoading || !chatInput.trim()}
                >
                  {chatLoading ? '发送中...' : '发送'}
                </BrutButton>
              </div>
            </BrutCard>
          </div>
        </BrutContainer>
      </main>
    </div>
  );
}
