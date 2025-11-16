import { useState } from 'react';
import { BrutButton, BrutCard, BrutInput } from './';
import { projectAPI } from '../services/api';
import { useProjectStore } from '../stores/projectStore';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * 创建项目模态框组件
 * 遵循 Neo-Brutalism 设计风格
 */
export default function CreateProjectModal({ isOpen, onClose }: CreateProjectModalProps) {
  const addProject = useProjectStore((state) => state.addProject);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    repositoryUrl: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      setError('项目名称不能为空');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await projectAPI.createProject({
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        repositoryUrl: formData.repositoryUrl.trim() || undefined,
      });

      if (response.data.code === 200) {
        // 添加到状态管理
        addProject(response.data.data);

        // 重置表单并关闭
        setFormData({ name: '', description: '', repositoryUrl: '' });
        onClose();
      } else {
        setError(response.data.message || '创建项目失败');
      }
    } catch (err: any) {
      console.error('Create project error:', err);
      const errorMessage = err.response?.data?.message || '创建项目失败，请重试';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({ name: '', description: '', repositoryUrl: '' });
      setError('');
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-brut-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <BrutCard className="max-w-lg w-full">
        <h3 className="brut-h3 mb-6">创建新项目</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 项目名称 */}
          <div>
            <label className="block font-bold mb-2" htmlFor="name">
              项目名称 <span className="text-brut-red">*</span>
            </label>
            <BrutInput
              id="name"
              name="name"
              type="text"
              placeholder="输入项目名称"
              value={formData.name}
              onChange={handleInputChange}
              required
              maxLength={100}
              disabled={loading}
            />
          </div>

          {/* 项目描述 */}
          <div>
            <label className="block font-bold mb-2" htmlFor="description">
              项目描述
            </label>
            <textarea
              id="description"
              name="description"
              placeholder="简要描述你的项目（可选）"
              value={formData.description}
              onChange={handleInputChange}
              maxLength={1000}
              disabled={loading}
              rows={3}
              className="w-full px-4 py-3 border-brut border-brut-black bg-brut-white
                       font-mono text-base focus:outline-none focus:ring-0
                       focus:shadow-brut-focus transition-shadow resize-none
                       disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>

          {/* 仓库URL */}
          <div>
            <label className="block font-bold mb-2" htmlFor="repositoryUrl">
              代码仓库URL
            </label>
            <BrutInput
              id="repositoryUrl"
              name="repositoryUrl"
              type="url"
              placeholder="https://github.com/username/repo （可选）"
              value={formData.repositoryUrl}
              onChange={handleInputChange}
              maxLength={500}
              disabled={loading}
            />
            <p className="text-xs text-brut-gray-600 mt-1">
              支持 GitHub、GitLab、Bitbucket 仓库链接
            </p>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="p-3 bg-brut-red text-brut-white font-bold border-brut border-brut-black">
              {error}
            </div>
          )}

          {/* 按钮组 */}
          <div className="flex gap-4 pt-4">
            <BrutButton
              type="button"
              variant="secondary"
              onClick={handleClose}
              disabled={loading}
              className="flex-1"
            >
              取消
            </BrutButton>
            <BrutButton
              type="submit"
              variant="primary"
              disabled={loading || !formData.name.trim()}
              className="flex-1"
            >
              {loading ? '创建中...' : '创建项目'}
            </BrutButton>
          </div>
        </form>
      </BrutCard>
    </div>
  );
}
