import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BrutButton, BrutCard, BrutContainer, CreateProjectModal } from '../components';
import { useAuthStore } from '../stores/authStore';
import { useProjectStore } from '../stores/projectStore';
import { projectAPI } from '../services/api';

/**
 * 主页 - 项目列表和管理
 */
export default function HomePage() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const { projects, setProjects } = useProjectStore();

  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await projectAPI.getProjects();
      setProjects(response.data.data || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleOpenProject = (projectId: number) => {
    navigate(`/project/${projectId}`);
  };

  return (
    <div className="min-h-screen bg-brut-gray-100">
      {/* 顶部导航栏 */}
      <header className="bg-brut-yellow border-b-brut border-brut-black shadow-brut-md">
        <BrutContainer>
          <div className="h-16 flex items-center justify-between">
            <h1 className="brut-h3">CODE ASSISTANT</h1>
            <div className="flex items-center gap-4">
              <span className="font-bold">你好, {user?.username}</span>
              <BrutButton
                variant="secondary"
                size="sm"
                onClick={handleLogout}
              >
                退出登录
              </BrutButton>
            </div>
          </div>
        </BrutContainer>
      </header>

      {/* 主内容区 */}
      <main className="py-8">
        <BrutContainer>
          <div className="flex justify-between items-center mb-8">
            <h2 className="brut-h2">我的项目</h2>
            <BrutButton
              variant="primary"
              onClick={() => setShowCreateModal(true)}
            >
              + 新建项目
            </BrutButton>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <p className="text-xl font-bold">加载中...</p>
            </div>
          ) : projects.length === 0 ? (
            <BrutCard className="text-center py-12">
              <h3 className="brut-h3 mb-4">还没有项目</h3>
              <p className="mb-6 text-lg">
                创建你的第一个项目,开始使用 AI 代码助手
              </p>
              <BrutButton
                variant="primary"
                onClick={() => setShowCreateModal(true)}
              >
                创建项目
              </BrutButton>
            </BrutCard>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <BrutCard key={project.id} variant="default">
                  <h3 className="brut-h4 mb-2">{project.name}</h3>
                  <p className="text-sm mb-4 line-clamp-2">
                    {project.description || '暂无描述'}
                  </p>
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold px-3 py-1 bg-brut-blue text-brut-white border-brut border-brut-black">
                      {project.status}
                    </span>
                    <BrutButton
                      size="sm"
                      variant="primary"
                      onClick={() => handleOpenProject(project.id)}
                    >
                      打开
                    </BrutButton>
                  </div>
                </BrutCard>
              ))}
            </div>
          )}
        </BrutContainer>
      </main>

      {/* 创建项目模态框 */}
      <CreateProjectModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
}
