import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BrutButton, BrutCard, BrutContainer } from '../components';
import { projectAPI } from '../services/api';
import { useAuthStore } from '../stores/authStore';

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

          {/* 操作按钮 */}
          <div className="flex gap-4">
            <BrutButton variant="primary" disabled>
              开始对话 (即将推出)
            </BrutButton>
            <BrutButton variant="secondary" disabled>
              重新索引 (即将推出)
            </BrutButton>
            <BrutButton variant="danger" disabled>
              删除项目 (即将推出)
            </BrutButton>
          </div>
        </BrutContainer>
      </main>
    </div>
  );
}
